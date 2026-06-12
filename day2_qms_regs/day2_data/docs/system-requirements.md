---
qms_version: 2.2.0
sop_id: CSC PR.001
sop_version: 2.0.1
template_id: CSC F.010
template_version: 2.0.1
record_version: 
record_id: SRS-001
title: System Requirements Specification
---

# System Requirements Specification

## General

|                           |               |
|---------------------------|---------------|
| **Template ID**           | CSC F.010     |
| **Template Version**      | 2.0.1         |
| **QMS Version**           | 2.2.0         |
| **SOP ID**                | CSC PR.001    |
| **SOP Version**           | 2.0.1         |
| **Regulatory References** |               |

|              |              |
|--------------|--------------|
| **Author**   |              |
| **Approval** |              |

### Purpose 
This purpose of this document is to describe what the {{device.name}} application must do. 

This document is meant to be read and agreed-upon by the project owners and the CSC team during design and development.

The document also provides traceability for software requirements throughout the project. 


### Scope

This document applies to {{device.name}} release {{device.version}}.

### Definitions

| Term    | Definition                                                                                   |
|---------|----------------------------------------------------------------------------------------------|
| SRS     | Software Requirements Spec                                                                   |
| SDS     | Software Design Spec                                                                         |


### Roles and Responsibilities
 
| Role             | Name(s) | Responsibilities                                                                                 |
|------------------|---------|--------------------------------------------------------------------------------------------------|
| Development lead |         | Completing documentation <br>  Gathering requirements <br >Organising meetings with stakeholders |
| Clinical lead    |         | Organising meetings with stakeholders <br>  Providing requirements                               |
| ML lead          |         | Providing requirements for ML activities.                                                        |

##### Stakeholders

The following stakeholders contributed to the requirements gathering process. 

| Name | Role |
|------|------|
|      |      |



### Introduction

{{device.name}} is intended to support osteoporosis and osteopenia screening from hand X-ray studies by calculating
Metacarpal Cortical Percentage (MCP) from suitable AP or PA images. The software receives DICOM hand X-rays, checks that
the image is suitable for processing, calculates MCP for the second metacarpal, and returns a DICOM encapsulated PDF
report to the source imaging study in PACS.

### Users

#### Clinicians

Clinicians use the report as decision support when reviewing patients who may need further osteoporosis or osteopenia
assessment. They expect the report to be returned to the imaging study, to clearly indicate whether processing succeeded,
and to avoid reporting MCP results for unsupported images.

#### Trust IT

Trust IT users support deployment, PACS integration, monitoring, and incident response. They expect the software to
handle DICOM inputs predictably, return outputs to the correct imaging study, and fail in a way that is visible to users.

### Use Environments

#### Radiology imaging workflow

Hand X-ray studies are acquired as part of routine care and stored in PACS. {{device.name}} processes eligible DICOM hand
X-rays from the imaging workflow and returns a DICOM encapsulated PDF report to the same imaging study.

#### Clinical review workflow

Clinicians review the returned report alongside the source images and other clinical information. The software output is
used as decision support and is not intended to replace clinical judgement.


### Use Cases 

#### Use Case #1

An AP or PA hand X-ray DICOM study with Modality CR or DX is available in PACS. {{device.name}} receives the study,
confirms that the image view is suitable, calculates MCP for the second metacarpal, generates a DICOM encapsulated PDF
report, and returns the report to the source imaging study within five minutes.

#### Use Case #2

An oblique hand X-ray, unsupported modality, abnormal anatomy, image artefact, or processing failure prevents reliable MCP
calculation. {{device.name}} does not return an MCP result as though processing succeeded. It safely fails out and returns
a DICOM encapsulated PDF report describing the failure state where technically possible.

### Considerations

The following list of considerations has been compiled from relevant suggestions from ISO 13485, BSI 62304 and BSI 62366:

- input data format to be processed.
- output format of the application
- destination of the output data
- the expected application/service uptime 
- the workload e.g. number of CTs per week.
- maximum acceptable turnaround time
- number and frequency of users to be supported
- user access 
- platform for delivery
- past complaints, failure reports, adverse events of similar products
- usability and maintenance
- security controls
- workflow integration
- local population demographics, to be reflected in training data.
- minimum sensitivity, specificity, true/false positive/negative rates.
- turnaround time for inference
- expected frequency of retraining.
- training data bias to acknowledge
- quality objectives for the project - e.g. quality metrics, ranges and thresholds
- contents of surveillance plan including metric to monitor once the application is deployed
- applicable regulatory requirements
- training requirements, such as workshops, training, documents etc.
- safety considerations for patients and staff
- information derived from similar/previous designs
- functional and capability requirements
- interfaces between systems
- software driven alarms, warnings and operator messages
- security requirements
- data definitions and database requirements
- installation and acceptance requirements of the delivered software at operation and maintenance site (* although this 
is GSTT only for projects built under this QMS)
- requirements related to methods of operation and maintenance
- requirements of IT network, Trust IT integration
- user maintenance requirements
- software update requirements

### User requirements

| Reference | Requirement title    | Requirements Description  | Priority |                                                                                                                           
|-----------|----------------------|---------------------------|----------|
{%- for requirement in requirements.requirements %} 
| {{ requirement.id }} | {{ requirement.title }} | {{ requirement.description }} |{{requirement.priority}}|
{%- endfor %}
