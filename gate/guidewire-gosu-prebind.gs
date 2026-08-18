package gw.job.velaru

uses gw.api.util.DisplayableException
uses java.io.BufferedReader
uses java.io.InputStreamReader
uses java.io.OutputStreamWriter
uses java.net.HttpURLConnection
uses java.net.URL
uses java.nio.charset.StandardCharsets

/**
 * PolicyCenter UI Bind door.
 *
 * Cloud API workers cannot see console Bind. Paste this class into gsrc, then call
 * assertBindAllowed(job) from the Bind checking set AND from the Bind PCF button
 * before JobProcess.bind() / bindAndIssue().
 *
 * Admin data first: UWIssueType code VelaruBlocksBind, blocking point Binding
 * (blocksBind). UWManagerReviewBlocksQuoteRelease is not enough.
 *
 * ScriptParameters (or env):
 *   VelaruGateURL  — live https Gate, never localhost
 *   VelaruGateKey  — Bearer key
 *   VelaruFuseId   — fuse on this book
 *   VelaruIssueType — default VelaruBlocksBind
 *
 * Guidewire Cloud: if Studio blocks raw HttpURLConnection, register GATE_URL as
 * Integration Gateway REST destination VelaruGate and swap callGate() to that.
 *
 * This class does not CHARGE. Approving the UW issue is not DEAD→LIVE.
 * Cloud API bind-only still needs the bind worker. This closes the console.
 */
class VelaruPreBind {

  static property get DefaultVerify() : String {
    return "https://velaru.xyz/verify"
  }

  static function assertBindAllowed(job : Job) {
    var result = hop(job)
    if (result.Allow) {
      return
    }
    raiseBlocksBind(job, result.VerifyUrl, result.Reason)
  }

  static function hop(job : Job) : VelaruHopResult {
    var out = new VelaruHopResult()
    out.Allow = false
    out.VerifyUrl = DefaultVerify
    out.Reason = "fail_closed"
    var gate = param("VelaruGateURL", "VELARU_GATE_URL")
    var key = param("VelaruGateKey", "VELARU_GATE_KEY")
    if (not gate.HasContent or not key.HasContent or isLocal(gate)) {
      out.Reason = "gate_not_public"
      return out
    }
    var fuse = param("VelaruFuseId", "VELARU_FUSE_ID")
    if (not fuse.HasContent) {
      fuse = "fuse_velaru_drill"
    }
    var jobId = job.JobNumber
    var payload = "{\"fuse_id\":\"" + jsonEscape(fuse) + "\",\"job_id\":\"" + jsonEscape(jobId) + "\",\"action\":\"ui-bind\"}"
    try {
      var json = postJson(gate.replaceAll("/$", "") + "/v1/pas/policycenter/pre-bind", key, payload)
      out.VerifyUrl = extractQuoted(json, "verify_url") ?: DefaultVerify
      var halted = json.contains("\"halt\":true") or json.contains("\"halt\": true")
      var allowed = json.contains("\"allow_bind\":true") or json.contains("\"allow_bind\": true")
      out.Allow = allowed and not halted
      out.Reason = out.Allow ? "live" : "dead_or_halt"
    } catch (e : Exception) {
      out.Allow = false
      out.Reason = "timeout_or_error"
    }
    return out
  }

  private static function raiseBlocksBind(job : Job, verifyUrl : String, reason : String) {
    var code = param("VelaruIssueType", "VELARU_ISSUE_TYPE")
    if (not code.HasContent) {
      code = "VelaruBlocksBind"
    }
    var issueType = UWIssueType.finder.findByCode(code)
    var receipt = "Velaru halted bind (" + reason + "). Receipt: " + verifyUrl + " Approve is not CHARGE."
    if (issueType != null) {
      var existing = job.UWIssues.firstWhere(\ i -> i.IssueType == issueType)
      if (existing == null) {
        var issue = new UWIssue(job)
        issue.IssueType = issueType
        issue.ShortDescription = "Velaru fuse halted bind"
        issue.LongDescription = receipt
        job.addToUWIssues(issue)
      }
    }
    throw new DisplayableException(receipt)
  }

  private static function postJson(url : String, key : String, payload : String) : String {
    var conn = new URL(url).openConnection() as HttpURLConnection
    conn.setRequestMethod("POST")
    conn.setDoOutput(true)
    conn.setConnectTimeout(4000)
    conn.setReadTimeout(4000)
    conn.setRequestProperty("Authorization", "Bearer " + key)
    conn.setRequestProperty("Content-Type", "application/json")
    conn.setRequestProperty("Accept", "application/json")
    var writer : OutputStreamWriter
    var reader : BufferedReader
    try {
      writer = new OutputStreamWriter(conn.OutputStream, StandardCharsets.UTF_8)
      writer.write(payload)
      writer.flush()
      var stream = conn.ResponseCode >= 400 ? conn.ErrorStream : conn.InputStream
      if (stream == null) {
        throw new DisplayableException("Velaru hop empty. Fail closed.")
      }
      reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8))
      var buf = new StringBuilder()
      var line = reader.readLine()
      while (line != null) {
        buf.append(line)
        line = reader.readLine()
      }
      return buf.toString()
    } finally {
      if (writer != null) writer.close()
      if (reader != null) reader.close()
      conn.disconnect()
    }
  }

  private static function param(scriptName : String, envName : String) : String {
    try {
      var sp = ScriptParameters.getParameterValue(scriptName)
      if (sp != null and (sp as String).HasContent) {
        return sp as String
      }
    } catch (ignored : Exception) {
    }
    return System.getenv(envName)
  }

  private static function isLocal(url : String) : boolean {
    var u = url.toLowerCase()
    return u.contains("localhost") or u.contains("127.0.0.1") or u.contains("0.0.0.0") or u.contains("[::1]")
  }

  private static function extractQuoted(json : String, key : String) : String {
    var marker = "\"" + key + "\":\""
    var i = json.indexOf(marker)
    if (i < 0) return null
    var start = i + marker.length
    var end = json.indexOf("\"", start)
    return end > start ? json.substring(start, end) : null
  }

  private static function jsonEscape(s : String) : String {
    return (s ?: "").replace("\\", "\\\\").replace("\"", "\\\"")
  }
}

class VelaruHopResult {
  var _allow : boolean as Allow
  var _verify : String as VerifyUrl
  var _reason : String as Reason
}

/*
 * BindCheckingSet.grs (Studio: Job → Bind checking set) — paste:

    gw.job.velaru.VelaruPreBind.assertBindAllowed(job)

 * Bind PCF button — same call immediately before bind.
 * Do not POST bind-only, bind-and-issue, or policy issue from this class.
 */
