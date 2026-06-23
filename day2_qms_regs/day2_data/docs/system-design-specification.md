---
qms_version: 2.2.0
sop_id: CSC PR.001
sop_version: 2.0.1
template_id: CSC F.019
template_version: 2.0.1
record_version: 
record_id: SDS-001
title: Software Design Specification
---

# Software Design Specification
<!-- [13485:7.3.2a,7.3.2e,7.3.3,7.3.4d]-->

## General

|                           |               |
|---------------------------|---------------|
| **Template ID**           | CSC F.019     |
| **Template Version**      | 2.0.1         |
| **QMS Version**           | 2.2.0         |
| **SOP ID**                | CSC PR.001    |
| **SOP Version**           | 2.0.1         |
| **Regulatory References** |               |


|              |              |
|--------------|--------------|
| **Author**   |              |
| **Approval** |              |

## Purpose

This document describes *how* {{device.name}} shall fulfil the requirements described in the software requirements
specification. It discusses the computation hardware the software will be expected run on, the software system's 
architecture, functional specifications associated with each software requirement, and user interface mock-ups.

It is written primarily for engineers working on {{device.name}}, who have the source code available, in addition to
this document.

## Scope

This document applies to {{device.name}} release {{device.version}}.


## Definitions

| Term  | Definition  |
|-------|-------------|
|       |             |
|       |             |

# System and Software Architecture Diagrams

The purpose of these diagrams are to present a high-level overview of the device design to facilitate a clear
understanding of

1. the software items and hardware components that make up the system
2. the relationships among them
3. the data inputs/outputs and flow of data among them
4. how users or external products, including IT infrastructure and peripherals, interact with the system.

[TODO: Add one or more diagrams to this section (e.g. block, state, flow, sequence) showing the functional units and
software items, focusing on the high-risk parts of the application. Clearly delineate any SOUP / off-the-shelf items.]

[[FDA-SW:ssad]]

## Software Items

[TODO: Enumerate the software items that make up {{device.name}}, and document the design of each one.]

### Software Item A

### Software Item B

## SOUP Software Items

This section enumerates the SOUP software items present within {{device.name}}.

{% for s in soup %}
### {{s.title}}

**Manufacturer:**
{% if s.manufacturer is defined %}
{{s.manufacturer}}
{% else %}
SOUP was developed collaboratively by the free open-source software community, and does not have a manufacturer in the
traditional sense.
{% endif %}
**Version:**

`{{s.version}}`
{% if device.BS62304_class != "A" %}
**Functional and Performance Requirements:**

{{s.purpose}}

**Hardware & Software Requirements:**
{% if s.requirements is defined %}
{{s.requirements}}
{% else %}
No noteworthy software or hardware requirements.
{% endif %}
**Known Anomalies:**
{% if s.anomaly_reference is not defined %}
Known anomaly list is not available.
{% else %}
{% if s.relevant_anomalies is not defined %}
No anomalies found that would result in incorrect behaviour for {{device.name}} leading to a hazardous situation.
{% else %}
{{s.anomalies}}
{% endif %}
**Open Anomaly List (Reference Only):**

`{{s.anomaly_reference}}`
{%- endif %}
{%- endif %}
{% endfor %}

## Functional Specifications

{% for spec in requirements.sys_des_spec %}

### {{spec.title}}

**Spec Item ID:** {{spec.id}}

**Description:** {{spec.description}}

**Mapped Requirement(s):** {{spec.linked_reqs}}

{% endfor %}



## User Interface Mockups

[TODO: If {{device.name}} has a user interface, add a sub-section per screen with a mock-up image, e.g.
`![Login screen](./images/uimockups/login.png)`. If there is no separate interactive UI, state that here.]
