#!/usr/bin/python
import os, sys, subprocess
import click
import requests
from time import sleep

@click.command()
@click.option('--url', prompt='Rancher server URL',
              help='The URL for your Rancher server, eg: http://rancher:8000')
@click.option('--key', prompt='API Key',
              help="The environment or account API key")
@click.option('--secret', prompt='API Secret',
              help="The secret for the access API key")
@click.option('--environment', default=None,
              help="The name of the environment to add the host into (if you have more than one)")
@click.option('--echo', default=False, is_flag=True,
              help="Print the docker run command to the console, instead of running it")
@click.option('--sudo', default=True, is_flag=True,
              help="Use sudo for docker run ...")
def main(url, key, secret, environment, echo, sudo):
    """Registers the current host with your Rancher server, creating the necessary registration keys."""
    # split url to protocol and host
    if "://" not in url:
        bail("The Rancher URL doesn't look right")

    proto, host = url.split("://")
    api = "%s://%s:%s@%s/v1" % (proto, key, secret, host)

    try:
        r = requests.get("%s/projects" % api)
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        bail("Couldn't connect to Rancher at %s - is the URL and API key right?" % host)
    else:
        environments = r.json()['data']

    if environment is None:
        environment = environments[0]['id']
    else:
        for e in environments:
            if e['id'].lower() == environment.lower() or e['name'].lower() == environment.lower():
                environment = e['id']

    if not environment:
        bail("Couldn't match your request to an environment on Rancher")

    try:
        r = requests.post("%s/registrationtokens?projectId=%s" % (
            api, environment
        ))
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        if environment:
            bail("Couldn't create a registration token for this host. Does your API key have access to the %s environment?" % environment)
        else:
            bail("Couldn't create a registration token for this host. Does your API key have the right permissions?")
    else:
        token = r.json()['id']

    active = False
    while not active:
        try:
            r = requests.get("%s/registrationtokens/%s" % (
                api, token
            ))
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            continue
        else:
            status = r.json()['state']
            if status.lower() == "active":
                command = r.json()['command']
                break

    if not command:
        bail("Cant register this host: Rancher didn't activate the new registration token.")

    if echo:
        msg(command)
    else:
        if not sudo:
            command = command.replace("sudo", '').strip()

        # run the docker command
        sys.exit(subprocess.call(command, shell=True))
        msg()

def msg(msg):
    click.echo(click.style(msg, fg='green'))

def bail(msg):
    click.echo(click.style('Error: ' + msg, fg='red'))
    sys.exit(1)
