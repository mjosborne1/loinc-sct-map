

1. Use this ECL expression to get all the Observable entities in the specified version of SNOMED CT 

   `{{url}}/ValueSet/$expand?url=http://snomed.info/sct/11010000107/version/20250721/fhir_vs=ecl/%3C%20363787002%20`
   
   Put the concept ids from the expansion into a pandas dataframe with the display

2. Iterate through the pandas data
   Use this GET request on terminology server endpoint to get all properties for each observable entity concept
   `{{url}}/CodeSystem/$lookup?version=http://snomed.info/sct/11010000107/version/20250921&code=168331010000106&property=*&system=http://snomed.info/sct`
   
   Response:

```json
{
    "resourceType": "Parameters",
    "parameter": [
        {
            "name": "code",
            "valueCode": "168331010000106"
        },
        {
            "name": "display",
            "valueString": "Hemoglobin [Mass/volume] in Blood"
        },
        {
            "name": "name",
            "valueString": "LOINC Extension module"
        },
        {
            "name": "system",
            "valueUri": "http://snomed.info/sct"
        },
        {
            "name": "version",
            "valueString": "http://snomed.info/sct/11010000107/version/20250921"
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "inactive"
                },
                {
                    "name": "value",
                    "valueBoolean": false
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "parent"
                },
                {
                    "name": "value",
                    "valueCode": "728771010000107"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "parent"
                },
                {
                    "name": "value",
                    "valueCode": "488291010000104"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "child"
                },
                {
                    "name": "value",
                    "valueCode": "142931010000103"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "child"
                },
                {
                    "name": "value",
                    "valueCode": "143151010000100"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "child"
                },
                {
                    "name": "value",
                    "valueCode": "67261010000101"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "child"
                },
                {
                    "name": "value",
                    "valueCode": "43401010000104"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "child"
                },
                {
                    "name": "value",
                    "valueCode": "41771010000104"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "child"
                },
                {
                    "name": "value",
                    "valueCode": "224941010000101"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "child"
                },
                {
                    "name": "value",
                    "valueCode": "66931010000104"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "child"
                },
                {
                    "name": "value",
                    "valueCode": "114821010000106"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "child"
                },
                {
                    "name": "value",
                    "valueCode": "185861010000101"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "child"
                },
                {
                    "name": "value",
                    "valueCode": "150481010000107"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "child"
                },
                {
                    "name": "value",
                    "valueCode": "145151010000101"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "child"
                },
                {
                    "name": "value",
                    "valueCode": "204891010000107"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "child"
                },
                {
                    "name": "value",
                    "valueCode": "198381010000105"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "child"
                },
                {
                    "name": "value",
                    "valueCode": "204121010000101"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "child"
                },
                {
                    "name": "value",
                    "valueCode": "103141010000106"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "sufficientlyDefined"
                },
                {
                    "name": "value",
                    "valueBoolean": true
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "effectiveTime"
                },
                {
                    "name": "value",
                    "valueString": "20250321"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "moduleId"
                },
                {
                    "name": "value",
                    "valueCode": "11010000107"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "normalFormTerse"
                },
                {
                    "name": "value",
                    "valueString": "===728771010000107+488291010000104:{704327008=(123038009:{370133003=256906008}),370130000=118539007,370132008=30766002,370134009=123029007,246093002=38082009}"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "normalForm"
                },
                {
                    "name": "value",
                    "valueString": "=== 728771010000107|Measurement of hemoglobin in blood|+488291010000104|Mass concentration of protein in blood at point in time|:{704327008|Direct site|=(123038009|Specimen|:{370133003|Specimen substance|=256906008|Blood material|}),370130000|Property|=118539007|Mass concentration (property)|,370132008|Scale type|=30766002|Quantitative value|,370134009|Time aspect|=123029007|Single point in time|,246093002|Component|=38082009|Hemoglobin|}"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "equivalentConcept"
                },
                {
                    "name": "value",
                    "valueCoding": {
                        "system": "http://loinc.org",
                        "code": "718-7"
                    }
                }
            ]
        },
        {
            "name": "designation",
            "part": [
                {
                    "name": "language",
                    "valueCode": "en"
                },
                {
                    "name": "use",
                    "valueCoding": {
                        "system": "http://snomed.info/sct",
                        "code": "900000000000013009",
                        "display": "Synonym"
                    }
                },
                {
                    "name": "value",
                    "valueString": "Hemoglobin (Bld) [Mass/Vol]"
                }
            ]
        },
        {
            "name": "designation",
            "part": [
                {
                    "name": "language",
                    "valueCode": "en"
                },
                {
                    "name": "use",
                    "valueCoding": {
                        "system": "http://terminology.hl7.org/CodeSystem/designation-usage",
                        "code": "display"
                    }
                },
                {
                    "name": "value",
                    "valueString": "Hemoglobin [Mass/volume] in Blood"
                }
            ]
        },
        {
            "name": "designation",
            "part": [
                {
                    "name": "language",
                    "valueCode": "en-x-sctlang-90000000-00005090-07"
                },
                {
                    "name": "use",
                    "valueCoding": {
                        "system": "http://terminology.hl7.org/CodeSystem/hl7TermMaintInfra",
                        "code": "preferredForLanguage",
                        "display": "Preferred For Language"
                    }
                },
                {
                    "name": "value",
                    "valueString": "Hemoglobin [Mass/volume] in Blood"
                }
            ]
        },
        {
            "name": "designation",
            "part": [
                {
                    "name": "language",
                    "valueCode": "en"
                },
                {
                    "name": "use",
                    "valueCoding": {
                        "system": "http://snomed.info/sct",
                        "code": "900000000000013009",
                        "display": "Synonym"
                    }
                },
                {
                    "name": "value",
                    "valueString": "Hemoglobin:MCnc:Pt:Bld:Qn"
                }
            ]
        },
        {
            "name": "designation",
            "part": [
                {
                    "name": "language",
                    "valueCode": "en"
                },
                {
                    "name": "use",
                    "valueCoding": {
                        "system": "http://snomed.info/sct",
                        "code": "900000000000013009",
                        "display": "Synonym"
                    }
                },
                {
                    "name": "value",
                    "valueString": "Mass concentration of hemoglobin in blood at point in time"
                }
            ]
        },
        {
            "name": "designation",
            "part": [
                {
                    "name": "language",
                    "valueCode": "en"
                },
                {
                    "name": "use",
                    "valueCoding": {
                        "system": "http://snomed.info/sct",
                        "code": "900000000000003001",
                        "display": "Fully specified name"
                    }
                },
                {
                    "name": "value",
                    "valueString": "Mass concentration of hemoglobin in blood at point in time (observable entity)"
                }
            ]
        },
        {
            "name": "property",
            "part": [
                {
                    "name": "code",
                    "valueCode": "609096000"
                },
                {
                    "name": "subproperty",
                    "part": [
                        {
                            "name": "code",
                            "valueCode": "370130000"
                        },
                        {
                            "name": "value",
                            "valueCode": "118539007"
                        },
                        {
                            "name": "valueCode",
                            "valueCode": "118539007"
                        }
                    ]
                },
                {
                    "name": "subproperty",
                    "part": [
                        {
                            "name": "code",
                            "valueCode": "704327008"
                        },
                        {
                            "name": "value",
                            "valueCode": "119297000"
                        },
                        {
                            "name": "valueCode",
                            "valueCode": "119297000"
                        }
                    ]
                },
                {
                    "name": "subproperty",
                    "part": [
                        {
                            "name": "code",
                            "valueCode": "370132008"
                        },
                        {
                            "name": "value",
                            "valueCode": "30766002"
                        },
                        {
                            "name": "valueCode",
                            "valueCode": "30766002"
                        }
                    ]
                },
                {
                    "name": "subproperty",
                    "part": [
                        {
                            "name": "code",
                            "valueCode": "246093002"
                        },
                        {
                            "name": "value",
                            "valueCode": "38082009"
                        },
                        {
                            "name": "valueCode",
                            "valueCode": "38082009"
                        }
                    ]
                },
                {
                    "name": "subproperty",
                    "part": [
                        {
                            "name": "code",
                            "valueCode": "370134009"
                        },
                        {
                            "name": "value",
                            "valueCode": "123029007"
                        },
                        {
                            "name": "valueCode",
                            "valueCode": "123029007"
                        }
                    ]
                }
            ]
        }
    ]
}
```

Get the LOINC code property from value where valueCoding.code = equivalentConcept

```json
{
    "name": "property",
    "part": [
        {
            "name": "code",
            "valueCode": "equivalentConcept"
        },
        {
            "name": "value",
            "valueCoding": {
                "system": "http://loinc.org",
                "code": "718-7"
            }
        }
    ]
}
```

3. output in a flat map file the source SNOMED CT code, display and the LOINC code. Leave LOINC Column empty if there is no match for the SNOMED Code.
