import click
import sys
from uuid import UUID
from csv2ved import csv2jpl_converter
from csv2ved import jpl2vad_converter
from csv2ved import vad2ved_converter


def print_data(data, indent=0):
    for key, value in data.items():
        isdict = isinstance(value, dict)
        printval = '' if isdict else value
        click.echo('{}{}: {}'.format(' ' * indent, click.style(key.replace("_", "-")),
                                     click.style(str(printval), fg='white')))
        if isdict:
            print_data(value, indent + 2)

    click.echo('')


def _handle_input_prompt(options):
    # if running without  --no-input option let the user review the configuration
    click.secho('\nrunning with options:', bold=True)
    print_data(options, indent=2)
    if not options['no_input']:
        try:
            click.confirm('Are you sure?', abort=True)
        except click.Abort:
            sys.exit('Aborting.')


def validate_company_cmd_line_parameter(company_id):
    try:
        UUID(company_id, version=4)
    except ValueError:
        return False
    return True


@click.command()
@click.option('--company-id', 'company_id', required=True, type=str, help='Company ID')
@click.option('--data-file', 'data_file', required=True, type=click.File('r'), help='path to partner data file in '
                                                                                    'csv format')
@click.option('--type-file', 'type_file', required=True, type=click.File('r'), help='path to data type file in '
                                                                                    'json format')
@click.option('--prod', default=True, type=bool, help='target environment for the generated environment. '
                                                      'Default is production')
@click.option('--no-input', default=False, is_flag=True, help='disables prompt before script runs')
def csv2ved(**opts):
    _handle_input_prompt(opts)

    if not validate_company_cmd_line_parameter(opts['company_id']):
        click.secho('Invalid format for company ID parameter, aborting', color='red')
        sys.exit(2)

    gpg_recipients = vad2ved_converter.GPG_PRODUCTION_RECIPIENTS
    gpg_key_data_directory = vad2ved_converter.GPG_PRODUCTION_KEY_DATA_DIRECTORY
    if not opts['prod']:
        gpg_recipients = vad2ved_converter.GPG_NON_PRODUCTION_RECIPIENTS
        gpg_key_data_directory = vad2ved_converter.GPG_NON_PRODUCTION_KEY_DATA_DIRECTORY

    gpg, init_error = vad2ved_converter.init_gpg(
        vad2ved_converter.GPG_HOME_DIRECTORY,
        gpg_recipients,
        gpg_key_data_directory
    )
    if init_error:
        click.secho(init_error, color='red')
        sys.exit(2)

    jpl_file_name, lines, errors = csv2jpl_converter.convert(opts['data_file'], opts['type_file'], opts['company_id'])
    if errors:
        click.secho('Errors: ')
        for error in errors:
            for line in error:
                click.secho("line {line}: {error}".format(line=line, error=error[line]))
        sys.exit(2)
    else:
        click.secho("{} lines written".format(lines))

    click.secho('Archiving ...')
    vad_filename, errors, jpl_bytes, vad_bytes = jpl2vad_converter.convert(jpl_file_name)
    if errors:
        click.secho('Errors occurred during compression: {}'.format(errors), color='red')
        sys.exit(2)

    click.secho('{jpl_file} archived to {vad_file}.'.format(jpl_file=jpl_file_name, vad_file=vad_filename))
    click.secho('Original file size: {jpl_bytes} bytes.'.format(jpl_bytes=jpl_bytes))
    click.secho('Compressed file size: {vad_bytes} bytes'. format(vad_bytes=vad_bytes))

    click.secho('Encrypting ...')

    ved_filename, status = vad2ved_converter.encrypt(gpg, vad_filename, gpg_recipients)

    if ved_filename is None:
        click.secho(status, color='red')
        sys.exit(2)
    else:
        click.secho('{vad_file} encrypted to {ved_file}, status: {status}'.format(
            vad_file=vad_filename, ved_file=ved_filename, status=status.status))


if __name__ == '__main__':
    csv2ved()
