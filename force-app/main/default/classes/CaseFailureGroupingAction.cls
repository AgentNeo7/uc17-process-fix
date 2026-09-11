public with sharing class CaseFailureGroupingAction {
 public class Request { @InvocableVariable(required=true) public Id caseId; }
 public class Result { @InvocableVariable public String groupKey; @InvocableVariable public Integer sampleCount; @InvocableVariable public String interpretation; }
 @InvocableMethod(label='Group Case Failure Signals' description='Groups requested visible Cases only. Reason/status association is not root cause.')
 public static List<Result> groupCases(List<Request> requests) {Set<Id> ids=new Set<Id>(); for(Request r:requests) if(r!=null && r.caseId!=null) ids.add(r.caseId);
  Map<Id,Case> rows=new Map<Id,Case>([SELECT Id,Reason,Status FROM Case WHERE Id IN :ids WITH USER_MODE]); Map<String,Integer> counts=new Map<String,Integer>(); Map<Id,String> keys=new Map<Id,String>();
  for(Case c:rows.values()) {String key=(String.isBlank(c.Reason)?'UNKNOWN':c.Reason)+'|'+c.Status; keys.put(c.Id,key); counts.put(key,(counts.containsKey(key)?counts.get(key):0)+1);}
  List<Result> out=new List<Result>(); for(Request r:requests) {Result v=new Result(); v.groupKey=r==null?null:keys.get(r.caseId); v.sampleCount=v.groupKey==null?0:counts.get(v.groupKey); if(v.groupKey==null) v.groupKey='UNLINKED'; v.interpretation='Association in requested Case sample; no causal conclusion'; out.add(v);} return out;
 }
}
