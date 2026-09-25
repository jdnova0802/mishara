// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * ClearanceEscrow — foreign vault for Gate clearance keepers.
 *
 * CUSTODY CLAIM (must stay true on every path):
 * - This contract holds USDC. Gate does not.
 * - Gate has NO callable admin role, NO pause, NO upgrade, NO sweep.
 * - Gate only produces EIP-712 Clear / Never signatures.
 * - Anyone may submit a valid signature; the contract verifies and pays.
 * - After expiry, principal reclaims WITHOUT any Gate signature.
 *
 * Honest residual (legal, not code): Gate's signing key still *authorizes*
 * release/liquidate when a valid sig is submitted. That is verifier-shaped,
 * not a wallet key — still get a legal opinion before real USDC.
 *
 * DO NOT deploy to mainnet without: independent audit, key-path review,
 * legal sanity check, and a full testnet dogfood with test USDC.
 */

interface IERC20 {
    function transferFrom(address from, address to, uint256 value) external returns (bool);
    function transfer(address to, uint256 value) external returns (bool);
}

contract ClearanceEscrow {
    IERC20 public immutable usdc;
    /// @dev ECDSA address whose EIP-712 signatures Gate produces. Immutable. Not a caller role.
    address public immutable gateSigner;
    uint16 public immutable defaultBountyBps;

    bytes32 private constant CLEAR_TYPEHASH =
        keccak256("Clear(bytes32 escrowId,bytes32 evidenceHash,uint64 deadline)");
    bytes32 private constant NEVER_TYPEHASH =
        keccak256(
            "Never(bytes32 escrowId,address keeper,bytes32 evidenceHash,uint64 deadline)"
        );

    enum Status {
        None,
        Open,
        Liquidated,
        Released,
        Reclaimed
    }

    struct Position {
        address principal;
        address agent;
        uint256 amount;
        uint16 bountyBps;
        bytes32 mandateHash;
        Status status;
        uint64 expiresAt;
    }

    mapping(bytes32 => Position) public positions;
    mapping(bytes32 => address) public liquidationWinner;
    mapping(bytes32 => bool) public usedEvidence; // replay guard

    event Locked(
        bytes32 indexed escrowId,
        address principal,
        address agent,
        uint256 amount,
        bytes32 mandateHash,
        uint64 expiresAt
    );
    event Released(bytes32 indexed escrowId, address to, uint256 amount, bytes32 evidenceHash);
    event Liquidated(
        bytes32 indexed escrowId,
        address keeper,
        uint256 bounty,
        uint256 residual,
        bytes32 evidenceHash
    );
    event Reclaimed(bytes32 indexed escrowId, address principal, uint256 amount);

    error BadStatus();
    error BadAmount();
    error Expired();
    error NotExpired();
    error BadSigner();
    error BadDeadline();
    error AlreadyTaken();
    error Replay();
    error NotPrincipal();

    constructor(address usdc_, address gateSigner_, uint16 bountyBps_) {
        require(usdc_ != address(0) && gateSigner_ != address(0), "zero");
        require(bountyBps_ <= 10_000, "bps");
        usdc = IERC20(usdc_);
        gateSigner = gateSigner_;
        defaultBountyBps = bountyBps_;
    }

    function DOMAIN_SEPARATOR() public view returns (bytes32) {
        return
            keccak256(
                abi.encode(
                    keccak256(
                        "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
                    ),
                    keccak256(bytes("ClearanceEscrow")),
                    keccak256(bytes("1")),
                    block.chainid,
                    address(this)
                )
            );
    }

    function lock(
        bytes32 escrowId,
        address agent,
        uint256 amount,
        bytes32 mandateHash,
        uint64 ttlSeconds
    ) external {
        if (amount == 0) revert BadAmount();
        if (ttlSeconds < 60) revert BadDeadline();
        if (positions[escrowId].status != Status.None) revert BadStatus();
        require(usdc.transferFrom(msg.sender, address(this), amount), "pull");
        uint64 expiresAt = uint64(block.timestamp) + ttlSeconds;
        positions[escrowId] = Position({
            principal: msg.sender,
            agent: agent,
            amount: amount,
            bountyBps: defaultBountyBps,
            mandateHash: mandateHash,
            status: Status.Open,
            expiresAt: expiresAt
        });
        emit Locked(escrowId, msg.sender, agent, amount, mandateHash, expiresAt);
    }

    /// Submit Gate Clear attestation. Caller can be anyone; funds go to principal.
    function release(
        bytes32 escrowId,
        bytes32 evidenceHash,
        uint64 deadline,
        bytes calldata signature
    ) external {
        Position storage p = positions[escrowId];
        if (p.status != Status.Open) revert BadStatus();
        if (block.timestamp > p.expiresAt) revert Expired();
        if (block.timestamp > deadline) revert BadDeadline();
        if (usedEvidence[evidenceHash]) revert Replay();

        bytes32 structHash = keccak256(
            abi.encode(CLEAR_TYPEHASH, escrowId, evidenceHash, deadline)
        );
        _requireGate(structHash, signature);

        usedEvidence[evidenceHash] = true;
        p.status = Status.Released;
        uint256 amt = p.amount;
        p.amount = 0;
        require(usdc.transfer(p.principal, amt), "push");
        emit Released(escrowId, p.principal, amt, evidenceHash);
    }

    /// Submit Gate Never attestation. Permissionless; first valid wins bounty to `keeper`.
    function liquidate(
        bytes32 escrowId,
        address keeper,
        bytes32 evidenceHash,
        uint64 deadline,
        bytes calldata signature
    ) external {
        if (keeper == address(0)) revert BadAmount();
        if (liquidationWinner[escrowId] != address(0)) revert AlreadyTaken();
        Position storage p = positions[escrowId];
        if (p.status != Status.Open) revert BadStatus();
        if (block.timestamp > p.expiresAt) revert Expired();
        if (block.timestamp > deadline) revert BadDeadline();
        if (usedEvidence[evidenceHash]) revert Replay();

        bytes32 structHash = keccak256(
            abi.encode(NEVER_TYPEHASH, escrowId, keeper, evidenceHash, deadline)
        );
        _requireGate(structHash, signature);

        usedEvidence[evidenceHash] = true;
        p.status = Status.Liquidated;
        liquidationWinner[escrowId] = keeper;
        uint256 bounty = (p.amount * uint256(p.bountyBps)) / 10_000;
        uint256 residual = p.amount - bounty;
        p.amount = 0;
        require(usdc.transfer(keeper, bounty), "bounty");
        require(usdc.transfer(p.principal, residual), "residual");
        emit Liquidated(escrowId, keeper, bounty, residual, evidenceHash);
    }

    /// Principal reclaim after expiry — NO Gate signature. Prevents Gate grief / key loss lockup.
    function reclaimExpired(bytes32 escrowId) external {
        Position storage p = positions[escrowId];
        if (p.status != Status.Open) revert BadStatus();
        if (msg.sender != p.principal) revert NotPrincipal();
        if (block.timestamp <= p.expiresAt) revert NotExpired();
        p.status = Status.Reclaimed;
        uint256 amt = p.amount;
        p.amount = 0;
        require(usdc.transfer(p.principal, amt), "push");
        emit Reclaimed(escrowId, p.principal, amt);
    }

    function _requireGate(bytes32 structHash, bytes calldata signature) internal view {
        bytes32 digest = keccak256(
            abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR(), structHash)
        );
        address recovered = _recover(digest, signature);
        if (recovered != gateSigner) revert BadSigner();
    }

    function _recover(bytes32 digest, bytes calldata sig) internal pure returns (address) {
        require(sig.length == 65, "siglen");
        bytes32 r;
        bytes32 s;
        uint8 v;
        assembly {
            r := calldataload(sig.offset)
            s := calldataload(add(sig.offset, 32))
            v := byte(0, calldataload(add(sig.offset, 64)))
        }
        if (v < 27) v += 27;
        require(v == 27 || v == 28, "v");
        // Reject malleable s
        require(
            uint256(s) <= 0x7fffffffffffffffffffffffffffffff5d576e7357a4501ddfe92f46681b20a0,
            "s"
        );
        address signer = ecrecover(digest, v, r, s);
        require(signer != address(0), "ecrecover");
        return signer;
    }

    // Explicitly absent by design (do not add):
    // - owner / admin
    // - pause / unpause
    // - upgrade / proxy
    // - setGateSigner
    // - rescueTokens / sweep
    // - Gate-as-msg.sender privileged calls
}
