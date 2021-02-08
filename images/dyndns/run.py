import argparse
import boto3
import requests
import sys

from botocore.exceptions import ClientError

AWS_CREDENTIAL_LOCATIONS = ["env", "profile"]


class CurrentIpRequestException(Exception):
    def __init__(self, message: str, original_exception: Exception):
        self.message = message
        self.original_exception = original_exception


class RecordReadException(Exception):
    def __init__(self, message: str, original_exception: Exception):
        self.message = message
        self.original_exception = original_exception


class RecordUpdateException(Exception):
    def __init__(self, message: str, original_exception: Exception):
        self.message = message
        self.original_exception = original_exception


# adding type hints for a boto3 client requires pulling in an entirely separate
# `boto3-stubs` module. not worth.
def get_domain_record_ip(client, zone_id: str, target_domain: str):
    more_items = True
    next_record = None
    record_set_list = []

    while more_items:
        try:
            if next_record:
                resp = client.list_resource_record_sets(
                    HostedZoneId=zone_id, StartRecordIdentifier=next_record
                )
            else:
                resp = client.list_resource_record_sets(HostedZoneId=zone_id)
        except ClientError as ce:
            code = ce.response["Error"]["Code"]
            msg = ce.response["Error"]["Message"]
            raise RecordReadException(message=f"{code}: {msg}", original_exception=ce)

        if resp["IsTruncated"]:
            next_record = resp["NextRecordIdentifier"]
        else:
            more_items = False

        record_set_list.extend(resp["ResourceRecordSets"])

    target_record = None
    for record_set in record_set_list:
        record_domain = record_set["Name"]

        # the record name from AWS contains a final dot. lets strip
        # it off, assuming the calling user didn't account for it.
        alt_record_domain = record_set["Name"][:-1]

        if target_domain == record_domain or target_domain == alt_record_domain:
            target_record = record_set
            break

    if target_record is None:
        raise RecordReadException(
            message=f"target domain ({target_domain}) could not be found within Route53 zone ({zone_id})",
            original_exception=None,
        )

    return target_record["ResourceRecords"][0]["Value"]


def get_public_ip():
    url = "http://ip4.me/api/"

    try:
        resp = requests.get(url=url)
    except Exception as ex:
        raise CurrentIpRequestException(
            message="Could not reach API for fetching current public IP",
            original_exception=ex,
        )

    if resp.status_code != 200:
        raise CurrentIpRequestException(
            message=f"Unexpected status code when fetching current public IP: {resp.status_code}",
            original_exception=None,
        )

    parts = resp.text.split(",")
    return parts[1]


def init_boto3(profile: str = None):
    if profile is None:
        return init_with_env()
    else:
        return init_with_profile(profile)


def init_with_env():
    return boto3.client("route53")


def init_with_profile(profile: str):
    session = boto3.session.Session(profile_name=profile)
    return session.client("route53")


# adding type hints for a boto3 client requires pulling in an entirely separate
# `boto3-stubs` module. not worth.
def update_domain(client, zone_id: str, target_domain: str, target_ip: str):
    try:
        client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Type": "A",
                            "TTL": 300,
                            "Name": target_domain,
                            "ResourceRecords": [{"Value": target_ip}],
                        },
                    }
                ],
            },
        )
    except ClientError as ce:
        code = ce.response["Error"]["Code"]
        msg = ce.response["Error"]["Message"]
        raise RecordUpdateException(message=f"{code}: {msg}", original_exception=ce)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--profile",
        help="The AWS profile name to utilize. If none is specified, boto3 will attempt to utilized environment variables.",
    )
    parser.add_argument(
        "-d", "--domain", help="the domain to update if required", required=True
    )
    parser.add_argument(
        "-z", "--zone", help="the Rout53 zone ID to utilize", required=True
    )
    args = parser.parse_args()

    client = init_boto3(args.profile)

    try:
        record_ip = get_domain_record_ip(client, args.zone, args.domain)
        public_ip = get_public_ip()

        if record_ip != public_ip:
            print(f"Public IP has changed. Updating Route53.")
            update_domain(client, args.zone, args.domain, public_ip)
        else:
            print(f"Route53 record is correct. No update required.")
    except CurrentIpRequestException as cire:
        print(f"Could not fetch current IP. {cire.message}")
    except RecordReadException as rre:
        print(f"Could not fetch A record for domain. {rre.message}")
    except RecordUpdateException as rue:
        print(f"Could not updated A record for domain. {rue.message}")