#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import os
from pprint import pprint
import requests
import sys
import yaml


def ripe_create(db, pwd, json_output, key, type, dryrun, object_entries):
    """
    Create non-existing RIPE object
    """
    if type == "route" or type == "route6":
        for i in object_entries:
            if list(i.keys())[0] == "origin":
                key = f"{key}{i['origin']}"

    # parameters for create request
    params = dict()
    params["password"] = pwd
    params["dry-run"] = dryrun

    url = f"{db}/ripe/{type}"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json; charset=utf-8",
    }
    r = requests.post(url, data=json_output, headers=headers)
    # print (r.text)
    eval_write_answer(r.status_code, r.text, dryrun)


def ripe_get(db, type, object, object_entries):
    """
    Get RIPE objects from the RIPE database
    """
    if type == "route" or type == "route6":
        for i in object_entries:
            if list(i.keys())[0] == "origin":
                object = f"{object}{i['origin']}"
    url = f"{db}/ripe/{type}/{object}?unfiltered"
    headers = {"Accept": "application/json"}
    r = requests.get(url, headers=headers)
    output = json.loads(r.text)
    return output


def ripe_update(db, pwd, json_output, key, type, dryrun, object_entries):
    """
    Update exsting RIPE object on the RIPE database
    """
    if type == "route" or type == "route6":
        for i in object_entries:
            if list(i.keys())[0] == "origin":
                key = f"{key}{i['origin']}"

    # parameters for update request
    params = dict()
    params["password"] = pwd
    params["dry-run"] = dryrun

    url = f"{db}/ripe/{type}/{key}"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json; charset=utf-8",
    }
    r = requests.put(url, data=json_output, params=params, headers=headers)
    eval_write_answer(r.status_code, r.text, dryrun)


def ripe_search(db, attribute, string):
    """
    Search object in the RIPE database
    """

    # common parameters - used for forward and reverse search
    params = dict()
    params["source"] = "ripe"
    params["query-string"] = string
    params["flags"] = ("no-filtering", "no-referenced")

    # if attribute given add to params dict - trigger inverse search
    if attribute:
        params["inverse-attribute"] = attribute

    url = f"{db}/search"
    headers = {"Accept": "application/json"}
    r = requests.get(url, params=params, headers=headers)
    output = json.loads(r.text)
    return output


def object_comparator_lookup(src_obj, dst_obj):
    """
    Compare an object with another entry by entry
    """
    dont_match = []
    no_upstream = []
    for i in dst_obj:
        count_name = 0
        count_value = 0
        for j in src_obj:
            if list(j.keys())[0] == list(i.keys())[0]:
                count_name = 1
                if j[list(j.keys())[0]] == i[list(i.keys())[0]]:
                    count_value = 1

        if count_name == 0:
            if list(i.keys())[0] != "last-modified":
                print(i.keys(), list(i.keys())[0])
                no_upstream.append(i)
        else:
            if count_value == 0:
                dont_match.append(i)

    if no_upstream or dont_match:
        return 1
    else:
        return 0


def object_comparator_strict(src_obj, dst_obj):
    """
    Compare an object with another entry by entry
    """
    for i in range(len(dst_obj)):
        if list(dst_obj[i].keys())[0] == "last-modified":
            del dst_obj[i]
            break
    dont_match = []
    failed_keys = 0
    failed_values = 0
    count = 0

    if len(src_obj) == len(dst_obj):
        for i in src_obj:
            if list(i.keys())[0] == list(dst_obj[count].keys())[0]:
                if (
                    i[list(i.keys())[0]]
                    != dst_obj[count][list(dst_obj[count].keys())[0]]
                ):
                    failed_values += 1
            else:
                failed_keys += 1
            count += 1
        if failed_keys or failed_values:
            return 1
        else:
            return 0

    else:
        return 1


def yaml_parser(objects):
    """
    TODO
    """
    a = open(objects, "r")
    objects = yaml.full_load(a.read())
    return objects


def eval_search(ripe_object, name, value):
    """
    Evaluate RIPE answer when searching objects
    """
    # print(ripe_object)
    try:
        error = ripe_object["errormessages"]["errormessage"][0]["text"]
        if error.find("101"):
            return 1
        else:
            return 2
    except:
        return 0


def eval_write_answer(status_code, text, dryrun):
    """
    Evaluate RIPE answer when writing objects
    """
    if dryrun:
        try:
            exists = json.loads(text)["errormessages"]["errormessage"][0]["text"]
        except:
            print(f"  RIPE answer: {text}")
        else:
            info = json.loads(text)["errormessages"]["errormessage"]
            for item in info:
                print(item["text"])
                if "args" in item:
                    print(item["args"][0]["value"])

    else:
        if status_code == 200:
            print("  RIPE answer: upstream object written")
        else:
            output = json.loads(text)["errormessages"]["errormessage"][0]["text"]
            print(f"  RIPE answer: {output}")


def yaml_to_json(yml_object):
    """
    Re-create RIPE json format from yaml
    """
    construct = {
        "objects": {
            "object": [{"source": {"id": "RIPE"}, "attributes": {"attribute": []}}]
        }
    }

    for i in yml_object:
        construct["objects"]["object"][0]["attributes"]["attribute"].append(
            {"name": list(i.keys())[0], "value": i[list(i.keys())[0]]}
        )
    return json.dumps(construct)


def json_to_yaml(json_payload):
    """
    Convert json to yaml
    """
    objects = {}

    for i in json_payload["objects"]["object"]:
        type = i["type"]
        primaryKey = i["primary-key"]["attribute"]
        objectKey = primaryKey[0]["value"]
        if type == "route" or type == "route6":
            origin = primaryKey[1]["value"]
            objectKey = f"{objectKey}{origin}"
        objects[objectKey] = []
        for j in i["attributes"]["attribute"]:
            if j["name"] != "last-modified":
                objects[objectKey].append(
                    {j["name"]: j["value"]}
                )
    yaml_out = yaml.dump(yaml.full_load(json.dumps(objects)), default_flow_style=False)
    return yaml_out


def ripe_normalize(ripe_obj):
    new_obj = []
    for i in ripe_obj:
        new_obj.append({i["name"]: i["value"]})

    return new_obj


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db", required=False, help="Database URL", default="https://rest.db.ripe.net"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--objects", required=False, help="Objects to compare / write")
    group.add_argument(
        "--search", required=False, help="Search for a particular string"
    )
    parser.add_argument(
        "--dryrun",
        required=False,
        action="store_true",
        help="Perform validation and not the upgrade",
    )
    parser.add_argument(
        "--pwd", required=False, help="Password needed to write objects"
    )
    parser.add_argument(
        "--attribute", required=False, help="Search for a specific attribute"
    )
    args = parser.parse_args()

    # if cmdline arguments for objects are given
    if args.objects:
        # check for password
        ## if not given via cmdline try env var -> exit on error
        if not args.pwd:
            try:
                pwd = os.environ["RIPE_PASSWORD"]
            except:
                print(f"no RIPE_PASSWORD environment variable found")
                print()
                parser.print_usage()
                if not args.dryrun:
                    sys.exit(1)
        else:
            pwd = args.pwd

        yml_objects = yaml_parser(args.objects)
        for key in yml_objects.keys():
            type = list(yml_objects[key][0].keys())[0]
            name = key
            print("")
            print(type, key)
            ripe_object = ripe_get(args.db, type, name, yml_objects[key])
            answer = eval_search(ripe_object, type, name)
            if answer == 0:
                ripe_object = ripe_object["objects"]["object"][0]["attributes"][
                    "attribute"
                ]
                ripe_obj = ripe_normalize(ripe_object)
                ripe_comparison = object_comparator_lookup(ripe_obj, yml_objects[key])
                local_comparison = object_comparator_lookup(yml_objects[key], ripe_obj)
                strict_comparison = object_comparator_strict(yml_objects[key], ripe_obj)

                if (
                    strict_comparison == 0
                    and ripe_comparison == 0
                    and local_comparison == 0
                ):
                    print(f"  Entries are consistent")
                else:
                    print(f"  Entries are not consistent")
                    pprint(yml_objects[key])
                    json_output = yaml_to_json(yml_objects[key])
                    ripe_update(
                        args.db,
                        pwd,
                        json_output,
                        key,
                        type,
                        args.dryrun,
                        yml_objects[key],
                    )

            if answer == 1:
                print(f"Object does not exists in the RIPE database")
                json_output = yaml_to_json(yml_objects[key])
                ripe_create(
                    args.db, pwd, json_output, key, type, args.dryrun, yml_objects[key]
                )

    # else if cmdline argument for search is given
    elif args.search:
        # inverse search for specific objects with specific attributes
        if args.attribute:
            search_results = ripe_search(args.db, args.attribute, args.search)
            answer = eval_search(search_results, args.attribute, args.search)
        # forward search for some object
        else:
            search_results = ripe_search(args.db, None, args.search)
            answer = eval_search(search_results, None, args.search)

        if answer == 0:
            print(json_to_yaml(search_results))
        else:
            sys.exit(1)

    # if neither search nor objects are given -> print usage
    else:
        parser.print_usage()
