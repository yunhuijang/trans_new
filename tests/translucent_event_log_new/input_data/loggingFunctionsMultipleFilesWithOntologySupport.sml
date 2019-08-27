
fun calculateTimeStamp() = 
let
    val curtimeint = IntInf.toLarge(time())*60;
    val curtime = SMLTime.fromSeconds(curtimeint);
    val curdate = Date.fromTimeLocal(curtime);
    val timestamp = (Date.fmt "%Y-%m-%dT%H:%M" curdate);

in
    timestamp^":"^"00.000+01:00"
end;



fun writeTimeStamp(file_id, timestamp) = 
let
    val _ = TextIO.output(file_id, "<Timestamp>")
    val _ = TextIO.output(file_id, timestamp)


in
    TextIO.output(file_id, "</Timestamp>\n")
end;


fun writeWorkflowValues(nil) = ">"
| writeWorkflowValues(workflowModelElement::nil) = ">" ^ workflowModelElement
| writeWorkflowValues(workflowModelElement::ontologicalConcepts::nil) = "modelReference = \"" ^ ontologicalConcepts ^ "\">" ^ workflowModelElement


fun writeWorkflowModelElement(file_id, workflowModelElement) = 
let
    val _ = TextIO.output(file_id, "<WorkflowModelElement ")
    val _ = TextIO.output(file_id, writeWorkflowValues(workflowModelElement))


in
    TextIO.output(file_id, "</WorkflowModelElement>\n")
end;


fun getEventTypeDescription(description) = 
    if length(description) = 0
    then ""
    else hd(description)

fun getOntologicalConcepts(event, description) = 
    if length(description) = 0
    then ""
    else if  event <> "unknown"
         then hd(description)
         else if length(description) < 2 
            then ""
            else hd(tl(description))


fun getComplement(event, description) = 
let
    val desc = getEventTypeDescription(description)
    val complement = "unknowntype = \"" ^ desc ^ "\""
    val ontologicalConcepts = getOntologicalConcepts(event,description)
    val sizeOntologicalConcepts = String.size ontologicalConcepts 
    val completementOntologicalConcepts = if  sizeOntologicalConcepts = 0 then "" else "modelReference = \""  ^ ontologicalConcepts ^ "\""
in
    if event = "unknown"
    then  complement ^ " " ^ completementOntologicalConcepts 
    else  completementOntologicalConcepts 
end;


fun writeEventType(file_id, event :: description) = 
let

    val complement = getComplement(event, description)
    val _ = TextIO.output(file_id, "<EventType ")
    val _ = TextIO.output(file_id, complement)
    val _ = TextIO.output(file_id, ">")     
    val _ = TextIO.output(file_id, event)

in
    TextIO.output(file_id, "</EventType>\n")
end;


fun writeOriginatorValues(nil) = ">"
| writeOriginatorValues(originator::nil) = ">" ^ originator 
| writeOriginatorValues(originator::ontologicalConcepts::nil) = "modelReference = \"" ^ ontologicalConcepts ^ "\">" ^ originator



fun writeOriginator(file_id, Originator) = 
let
    val _ = TextIO.output(file_id, "<Originator ")
    val _ = TextIO.output(file_id, writeOriginatorValues(Originator)) 

in
    TextIO.output(file_id, "</Originator>\n")
end;


fun writeDataAttributes(nil) = ""
| writeDataAttributes(name::nil) =  "<Attribute name = \"" ^ name ^ "\"> </Attribute>\n" 
| writeDataAttributes(name::ontologicalConcepts::value::tail) = "<Attribute name = \"" ^ name ^ "\" modelReference = \"" ^ ontologicalConcepts ^ "\">" ^value ^" </Attribute>\n" ^ writeDataAttributes(tail) 

fun writeData(file_id, data) = 
let
    val _ = TextIO.output(file_id, "<Data>\n")
    val _ = TextIO.output(file_id, writeDataAttributes(data))
in
    TextIO.output(file_id, "</Data>\n")
end;      

fun  testWriteData (file_id, data) = 
    if length(data) = 0
    then TextIO.output(file_id, "")
    else writeData(file_id, data)

fun add (file_id, workflowModelElement, EventType, TimeStamp, Originator, Data)=
let
    val _ = TextIO.output(file_id, "<AuditTrailEntry>\n")
    val _ = testWriteData(file_id, Data)
    val _ = writeWorkflowModelElement(file_id, workflowModelElement)
    val _ = writeEventType(file_id, EventType)
    val _ = writeTimeStamp(file_id, TimeStamp)
    val _ = writeOriginator(file_id, Originator)
    val _ = TextIO.output(file_id, "</AuditTrailEntry>\n")

in
    TextIO.closeOut(file_id)
end;



fun addATE (caseID,workflowModelElement, EventType, TimeStamp, Originator, Data) = 
let
    val file_id = TextIO.openAppend(FILE^Int.toString(caseID)^FILE_EXTENSION)
in
    add(file_id, workflowModelElement, EventType, TimeStamp, Originator, Data)
end;


fun createCaseFile(caseID, data) = 
let
   val caseIDString = Int.toString(caseID)
   val file_id = TextIO.openOut(FILE ^ caseIDString  ^ FILE_EXTENSION)
   val _ = TextIO.output(file_id, caseIDString  ^ "\n")
   val _ = writeData(file_id, data)
in
   TextIO.closeOut(file_id)
end;




