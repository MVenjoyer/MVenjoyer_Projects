import click
from encode import encode_message
from decode import decode_message


@click.group()
def cli():
    """steganography"""
    pass


@click.command()
@click.argument('data')
@click.argument('message')
def encode(data, message):
    """encode"""
    enc_message = encode_message(data, message)
    click.echo(f'encoded message: {enc_message}')


@click.command()
@click.argument('data')
def decode(data):
    """decode"""
    dec_message = decode_message(data)
    click.echo(f'decoded message: {dec_message}')


cli.add_command(encode)
cli.add_command(decode)

if __name__ == '__main__':
    cli()
