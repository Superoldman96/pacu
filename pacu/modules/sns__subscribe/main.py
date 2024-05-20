#!/usr/bin/env python3
import argparse
import re

from pacu.core.lib import strip_lines
from pacu import Main

module_info = {
    "name": "sns__subscribe",
    "author": "h00die & 6a6f656c of nDepth Security",
    "category": "LATERAL_MOVE",  # or maybe persistence? kind of depends what may come over the topic, like creds
    "one_liner": "Subscribe to a Simple Notification Service (SNS) topic",
    "description": strip_lines(
        """
        This module will attempt to subscribe to a topic (arn) via an email address.
        """
    ),
    "services": ["SNS"],
    "prerequisite_modules": [],
    "arguments_to_autocomplete": [],
}

parser = argparse.ArgumentParser(add_help=False, description=module_info["description"])

parser.add_argument(
    "--topic",
    required=True,
    default=False,
    help=strip_lines(
        """
    Topic ARN to subscribe to. Typically in the format arn:aws:sns:<region>:<client_id>:<topic_name>.
    """
    ),
)
parser.add_argument(
    "--email",
    required=True,
    default=None,
    help=strip_lines(
        """
    Email address to subscribe to the topic
    """
    ),
)


def main(args, pacu_main: "Main"):
    session = pacu_main.get_active_session()

    # Don't modify these. They can be removed if you are not using the function.
    args = parser.parse_args(args)
    print = pacu_main.print

    key_info = pacu_main.key_info
    fetch_data = pacu_main.fetch_data
    # End don't modify

    # https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

    if not (re.fullmatch(email_regex, args.email)):
        print("  Please use a valid email address for email parameter\n")
        return

    if not args.topic.startswith("arn:aws:sns:"):
        print(
            "  Please use a valid topic, typical format is arn:aws:sns:<region>:<client_id>:<topic_name>\n"
        )
        return

    client = pacu_main.get_boto3_client("sns")

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/subscribe.html
    try:
        response = client.subscribe(
            TopicArn=args.topic,
            Protocol="email",
            Endpoint=args.email,
            ReturnSubscriptionArn=True,
        )
        print(
            "Subscribed successfully, check email for subscription confirmation. Confirmation ARN: {}".format(
                response["SubscriptionArn"]
            )
        )
    except Exception as error:
        print(
            "Unable to subscribe, check permissions and topic. Error: {}".format(error)
        )
