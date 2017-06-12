#!/usr/bin/python3

import click
from pdc_client import PDCClient
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def get_modulemd(module_name, stream):
    """
    Check if module and stream are built successfully on PDC server
    """
    pdc_server = "https://pdc.fedoraproject.org/rest_api/v1/unreleasedvariants"
    #Using develop=True to not authenticate to the server
    pdc_session = PDCClient(pdc_server, ssl_verify=True, develop=True)
    pdc_query = dict(
        variant_id = module_name,
        variant_version = stream,
        fields="modulemd",
        ordering="variant_release",
        #active=True returns only succesful builds
        active = True,
    )
    try:
        mod_info = pdc_session(**pdc_query)
    except Exception as ex:
        raise IOError("Could not query PDC server for %s (stream: %s) - %s" % (
                       module_name, stream, ex))
    if not mod_info or "results" not in mod_info.keys() or not mod_info["results"]:
        raise IOError("%s (stream: %s) is not available on PDC" % (
                       module_name, stream))
    return mod_info["results"][-1]["modulemd"]

@click.command()
@click.option('--module', default='base-runtime',
              help='The module to get the API from')
@click.option('--ref', default='f26',
              help='The ref of the module to retrieve')
def main(module, ref):
    modulemd = yaml.load(get_modulemd(module, ref), Loader=Loader)

    for rpm in sorted(modulemd['data']['api']['rpms']):
        print(rpm)


if __name__ == "__main__":
    main()
