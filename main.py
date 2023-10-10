import argparse
import asyncio
import logging
import pathlib
from aiofiles import open
from zlib import compressobj, decompressobj


async def decode(orig_path):
    async with open(orig_path, mode='rb') as save_file:
        byte_arr = await save_file.read()
    obj = decompressobj(wbits=-15)
    data = obj.decompress(byte_arr)
    async with open(f'Edit_File.json', mode='wb') as write_file:
        await write_file.write(data)
    logging.info(f'Edit_File.json has been written to disk.')


async def encode(new_path):
    async with open(new_path, mode='rb') as edit_file:
        save_data = await edit_file.read()
    obj = compressobj(wbits=-15)
    async with open(f'Edited_Save_File.nson', mode='wb') as new_save:
        await new_save.write(obj.compress(save_data))
    logging.info(f'Edited_Save_File.nson has been written to disk.')


async def cmdhandler(cmd, orig_path):
    try:
        if orig_path.suffix == '.nson' and cmd == '-decode':
            await decode(orig_path)
        elif orig_path.suffix == '.json' and cmd == '-encode':
            await encode(orig_path)
        else:
            raise ValueError
    except FileExistsError:
        logging.error(f'{orig_path.parent}/Edit_File.json already exists.')
    except FileNotFoundError:
        logging.error(f'{orig_path} does not exist.')
    except IsADirectoryError:
        logging.error(f'{orig_path} is a directory.')
    except PermissionError:
        logging.error(f'Permission error, lack of read / write access.')
    except ValueError:
        logging.error(f'Wrong file format. Expected: {"-decode" if cmd == "-encode" else "-encode"}')


async def main():
    parser = argparse.ArgumentParser(description='Encode or decode files.')
    parser.add_argument('cmd', choices=['-encode', '-decode'], help='Command to execute')
    parser.add_argument('filename', type=pathlib.Path, help='File to encode or decode')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        await cmdhandler(args.cmd, args.filename)
    except Exception as ex:
        logging.error(f'Exception type - {type(ex)}\tException args - {ex.args}\tException - {ex}')


if __name__ == '__main__':
    asyncio.run(main())
