package gw.job.velaru

uses gw.api.util.DisplayableException

/**
 * PolicyCenter renewal auto-bind door.
 *
 * Some renewals bind at midnight with no Cloud API call and no UI click.
 * The bind worker never sees that write. Insert this as a workflow Gosu step
 * BEFORE the Bind / auto-bind activity on RenewalWF (and any product-specific
 * renewal workflow that can bind without a person).
 *
 *   gw.job.velaru.VelaruRenewalPreBind.assertBeforeAutoBind(job)
 *
 * Requires VelaruPreBind (guidewire-gosu-prebind.gs) in the same package.
 * Same ScriptParameters. Same VelaruBlocksBind UW issue type (blocksBind).
 *
 * This is not CHARGE. Workflow continue-on-error must be off — fail closed.
 * Parent/child org kill is a Velaru engine fact, not something this step fakes.
 */
class VelaruRenewalPreBind {

  static function assertBeforeAutoBind(job : Job) {
    if (not (job typeis Renewal)) {
      return
    }
    VelaruPreBind.assertBindAllowed(job)
  }

  static function workflowStep(wf : Object) {
    var job : Job = extractJob(wf)
    if (job == null) {
      throw new DisplayableException("Velaru renewal hop: no Job on workflow. Fail closed. https://velaru.xyz/verify")
    }
    assertBeforeAutoBind(job)
  }

  private static function extractJob(wf : Object) : Job {
    try {
      var typed = wf as Workflow
      if (typed.Job != null) {
        return typed.Job
      }
    } catch (ignored : Exception) {
    }
    return null
  }
}

/*
 * RenewalWF.xml — add a Gosu step immediately before Bind/AutoBind:

    <Step id="VelaruPreBind">
      <Gosu>
        gw.job.velaru.VelaruRenewalPreBind.workflowStep(wf)
      </Gosu>
      <NextStep ref="Bind"/>
    </Step>

 * If your workflow uses AutoIssue after Bind, hop before Bind, not after.
 * Bound with no documents is already a spent world.
 *
 * Do not set continue-on-error. Timeout = halt. LIVE hop is the only pass.
 */
