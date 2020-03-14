from rdflib import Graph
import rdflib
# Types
from typing import Dict, NamedTuple, Set, OrderedDict
import re
import csv

EMPTY="null"
PID = 'pid'
Person = NamedTuple(
    "Person",
    [
        ('pid', str),
        ("firstname", str),
        ("lastname", str),
        ("job_title", str),
        ("homepage", str),
        ("works_at_name", str),
        ("works_at_url", str),
        ("works_on_name", str),
        ("works_on_url", str),
        ("works_on_decs", str),
        ("from_", str),
    ],
)

EP = Person(
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY
)

Other = NamedTuple(
    "Other", [('pid', str), ("name", str), ("url", str), ("decs", str)],
)

EO = Other(EMPTY, EMPTY, EMPTY, EMPTY)
def processID(uristring):
    if uristring == 'null':
        return 'null'
    else:
        pond = uristring.find('#')
        end = uristring.find("'")
        return uristring[pond+1:]


def build_others() -> Dict[str, Other]:
    """Build others cache."""
    return dict(
        map(
            lambda other: (
                lambda otherd: (
                    str(otherd.get('pid', EMPTY)),
                    Other(
                        str(otherd.get('pid', EMPTY)),
                        str(
                            otherd.get(
                                "name",
                                otherd.get(
                                    "title", otherd.get("label", EMPTY)
                                ),
                            )
                        ),
                        str(otherd.get("url", otherd.get("url2", EMPTY))),
                        str(otherd.get("desc", EMPTY)),
                    ),
                )
            )(other.asdict()),
            G.query(
                "select distinct ?pid ?name ?title ?label ?url ?url2 ?desc "
                "where {"
                "{?pid rdf:type <http://xmlns.com/foaf/0.1/Organization>} "
                "union {"
                "?pid rdf:type ?core "
                "filter "
                "(regex(str(?core), 'http://vivoweb.org/ontology/core'))"
                "} union {"
                "?pid rdf:type ?report "
                "filter "
                "(regex(str(?report), 'http://purl.org/ontology/bibo'))"
                "} union {"
                "?pid rdf:type ?other "
                "filter "
                "(regex(str(?other), 'http://semanticscience.org/resource'))"
                "} . "
                "optional {?pid sdso:mayAnswer ?qid} "
                "optional {?pid <http://xmlns.com/foaf/0.1/name> ?name} "
                "optional {?pid <http://purl.org/dc/terms/title> ?title} "
                "optional {?pid rdfs:label ?label} "
                "optional {"
                "?pid <http://dev.poderopedia.com/vocab/hasURL> ?url"
                "} "
                "optional {"
                "?pid sdso:hasDocumentURL ?url2"
                "} "
                "optional {"
                "?pid <http://purl.org/dc/terms/description> ?desc"
                "} "
                "}",
            ),
        )
    )


def get_works(works_at_id: str, works_on_id: str) -> Dict[str, str]:
    """Get works information by works pid."""
    return (
        lambda works_at, works_on: {
            "works_at_name": works_at.name,
            "works_at_url": works_at.url,
            "works_on_name": works_on.name,
            "works_on_url": works_on.url,
            "works_on_decs": works_on.decs,
        }
    )(build_others().get(works_at_id, EO), build_others().get(works_on_id, EO))


if __name__ == '__main__':
    G = Graph().parse('../data/SDS-OKN_20200301_CleanOntology_InstanceTurtle_PJM_3PM.owl', format="n3")  # noqa: WPS111
    pa = G.query(
        "select ?pid "
        "?may_Answer "
        "where {"
        "?pid rdf:type <http://xmlns.com/foaf/0.1/Person> . "
        "optional {?pid sdso:mayAnswer ?may_Answer } "
        "} "
        "order by ?pid"
    )
    with open('../data/person_question_relation.csv', mode='w') as fin:
        fin.write("person_id,question_id\n")
        for i in pa:
            padict = i.asdict()
            pid = processID(padict.get('pid', EMPTY))
            aid = processID(padict.get('may_Answer', EMPTY))
            fin.write(pid+','+aid+'\n')

    people = dict(
        map(
            lambda person: (
                lambda persond: (
                    str(persond.get(PID, EMPTY)),
                    (
                        Person(
                            str(persond.get(PID, EMPTY)),
                            str(persond.get("firstname", EMPTY)),
                            str(persond.get("lastname", EMPTY)),
                            " ".join(
                                re.findall(  # handle
                                    # Scientist-Ecosystem or
                                    # ScientistEcosystem to
                                    r"([A-Z][a-z,]*)",
                                    #  Scientist Ecosystem
                                    str(persond.get("job_title", EMPTY)),
                                )
                            ),
                            str(persond.get("homepage", EMPTY)),
                            from_=EMPTY,
                            **get_works(
                                str(persond.get("works_at", EMPTY)),
                                str(persond.get("works_on", EMPTY)),
                            ),
                        )
                    ),
                )
            )(person.asdict()),
            G.query(
                "select ?pid "
                "?firstname ?lastname ?job_title "
                "?homepage ?works_on ?works_at ?qid "
                "where {"
                "?pid rdf:type <http://xmlns.com/foaf/0.1/Person> . "
                "optional {?pid sdso:holdsJobTitle ?job_title } "
                "optional {?pid sdso:worksAt ?works_at } "
                "optional {?pid sdso:worksOn ?works_on } "
                "optional {"
                "?pid <http://xmlns.com/foaf/0.1/firstName> ?firstname "
                "} "
                "optional {"
                "?pid <http://xmlns.com/foaf/0.1/homepage> ?homepage "
                "} "
                "optional {"
                "?pid <http://xmlns.com/foaf/0.1/lastName> ?lastname "
                "} "
                "} "
                "order by ?pid"
            ),
        )
    )
    with open('../data/person_info.csv.csv', mode='w') as fin:
        writer = csv.writer(fin)
        writer.writerow(('pid','firstname','lastname','job_title','homepage','works_at_name','works_at_url','works_on_name','works_on_url','works_on_decs','from_'))
        prices = list(people.values())
        for i in prices:
            writer.writerow([processID(i.pid),i.firstname, i.lastname, i.job_title, i.homepage, i.works_at_name, i.works_at_url,
                           i.works_on_name,i.works_on_url,i.works_on_decs,i.from_])


    questions = G.query(
        "select ?qid "
        "?ntk_Text ?has_NTKTopic ?collection_Instrument ?addresses_to "
        "where {"
        "?qid rdf:type sdso:NeedToKnowQuestion . "
        "optional {?qid sdso:ntkText ?ntk_Text } "
        "optional {?qid sdso:hasNTKTopic ?has_NTKTopic } "
        "optional {?qid sdso:collectionInstrument ?collection_Instrument } "
        "optional {?qid sdso:addresses ?addresses_to } "
        "} "
        "order by ?qid"
    )
    with open('../data/question_info.csv', mode='w') as fin:
        fin.write("qid,ntk_Text,hasNTKTopic,collectionInstrument,addresses")
        for i in questions:
            dict = i.asdict()
            pid = processID(dict.get('qid', EMPTY))
            text = processID(dict.get('ntk_Text', EMPTY))
            has_NTKTopic = processID(dict.get('has_NTKTopic', EMPTY))
            collection_Instrument = processID(dict.get('collection_Instrument', EMPTY))
            addresses_to = processID(dict.get('addresses_to', EMPTY))
            fin.write(pid + ',' + text +',' + has_NTKTopic + ','+ collection_Instrument+ ','+ addresses_to +'\n')

