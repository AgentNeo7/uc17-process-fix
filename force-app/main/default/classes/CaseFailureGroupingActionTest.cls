@IsTest private class CaseFailureGroupingActionTest {
 @IsTest static void duplicatesDoNotInflateCounts() {Case c=new Case(Subject='Synthetic',Status='New',Origin='Phone');insert c;CaseFailureGroupingAction.Request r=new CaseFailureGroupingAction.Request();r.caseId=c.Id;List<CaseFailureGroupingAction.Result> out=CaseFailureGroupingAction.groupCases(new List<CaseFailureGroupingAction.Request>{r,r});System.assertEquals(2,out.size());System.assertEquals(1,out[0].sampleCount);System.assert(out[0].groupKey.startsWith('UNKNOWN|'));}
 @IsTest static void missingCaseUnlinked() {CaseFailureGroupingAction.Result v=CaseFailureGroupingAction.groupCases(new List<CaseFailureGroupingAction.Request>{null})[0];System.assertEquals('UNLINKED',v.groupKey);System.assertEquals(0,v.sampleCount);}
}
