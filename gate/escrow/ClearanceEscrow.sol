// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * ClearanceEscrow — foreign vault for Gate clearance keepers.
 *
 * Gate NEVER holds these funds. This contract holds USDC.
 * Release requires a Gate Clear attestation (bytes evidenceHash + clearOk).
 * Breach: anyone may liquidate with Gate Never/NO_GO evidence; first wins bounty.
 *
 * Massive ingress: permissionless lockUSDC. No Gate checkout. No Gate MTL.
 * Deploy, set GATE_ESCROW_* env on Gate index, agents park capital here.
 */

interface IERC20 {
    function transferFrom(address from, address to, uint256 value) external returns (bool);
    function transfer(address to, uint256 value) external returns (bool);
}

contract ClearanceEscrow {
    IERC20 public immutable usdc;
    address public gateAttestor; // Ed25519/ECDSA verifier adapter or multisig that Gate drives
    uint16 public defaultBountyBps; // e.g. 500 = 5%

    enum Status { None, Open, Liquidated, Released }

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

    event Locked(bytes32 indexed escrowId, address principal, address agent, uint256 amount, bytes32 mandateHash);
    event Released(bytes32 indexed escrowId, address to, uint256 amount);
    event Liquidated(bytes32 indexed escrowId, address keeper, uint256 bounty, uint256 residual, bytes32 evidenceHash);

    error BadStatus();
    error BadAmount();
    error Expired();
    error NotAttestor();
    error AlreadyTaken();

    constructor(address usdc_, address gateAttestor_, uint16 bountyBps_) {
        require(usdc_ != address(0) && gateAttestor_ != address(0), "zero");
        require(bountyBps_ <= 10_000, "bps");
        usdc = IERC20(usdc_);
        gateAttestor = gateAttestor_;
        defaultBountyBps = bountyBps_;
    }

    function lock(
        bytes32 escrowId,
        address agent,
        uint256 amount,
        bytes32 mandateHash,
        uint64 ttlSeconds
    ) external {
        if (amount == 0) revert BadAmount();
        if (positions[escrowId].status != Status.None) revert BadStatus();
        require(usdc.transferFrom(msg.sender, address(this), amount), "pull");
        positions[escrowId] = Position({
            principal: msg.sender,
            agent: agent,
            amount: amount,
            bountyBps: defaultBountyBps,
            mandateHash: mandateHash,
            status: Status.Open,
            expiresAt: uint64(block.timestamp) + ttlSeconds
        });
        emit Locked(escrowId, msg.sender, agent, amount, mandateHash);
    }

    /// Gate Clear path — attestor says GO; principal/agent receives funds.
    function release(bytes32 escrowId, bytes32 clearEvidenceHash) external {
        if (msg.sender != gateAttestor) revert NotAttestor();
        Position storage p = positions[escrowId];
        if (p.status != Status.Open) revert BadStatus();
        p.status = Status.Released;
        uint256 amt = p.amount;
        p.amount = 0;
        require(usdc.transfer(p.principal, amt), "push");
        emit Released(escrowId, p.principal, amt);
        clearEvidenceHash; // attestation bound off-chain / in adapter
    }

    /// Keeper path — Gate Never/NO_GO evidence; first caller with valid attestor sig wins.
    /// Minimal version: attestor calls liquidate for the winning keeper (or adapter verifies EIP-712).
    function liquidate(
        bytes32 escrowId,
        address keeper,
        bytes32 evidenceHash
    ) external {
        if (msg.sender != gateAttestor) revert NotAttestor();
        if (liquidationWinner[escrowId] != address(0)) revert AlreadyTaken();
        Position storage p = positions[escrowId];
        if (p.status != Status.Open) revert BadStatus();
        p.status = Status.Liquidated;
        liquidationWinner[escrowId] = keeper;
        uint256 bounty = (p.amount * uint256(p.bountyBps)) / 10_000;
        uint256 residual = p.amount - bounty;
        p.amount = 0;
        require(usdc.transfer(keeper, bounty), "bounty");
        require(usdc.transfer(p.principal, residual), "residual");
        emit Liquidated(escrowId, keeper, bounty, residual, evidenceHash);
    }
}
