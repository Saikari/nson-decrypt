from zlib import compressobj, decompressobj
from os import path
from aiofiles import open
from asyncio import run
import pytest

async def decode(orig_path):
    async with open(orig_path, mode='rb') as save_file:
        byte_arr = await save_file.read()
    obj = decompressobj(wbits=-15)
    data = obj.decompress(byte_arr)
    async with open(f'Edit_File.json', mode='wb') as write_file:
        await write_file.write(data)
    print(f'Edit_File.json has been written to disk.')


async def encode(new_path):
    async with open(new_path, mode='rb') as edit_file:
        save_data = await edit_file.read()
    obj = compressobj(wbits=-15)
    async with open(f'Edited_Save_File.nson', mode='wb') as new_save:
        await new_save.write(obj.compress(save_data))
    print(f'Edited_Save_File.nson has been written to disk.')


async def cmdhandler(cmd):
    orig_path = input(f'Please enter {".nson" if cmd =="-decode" else ".json"} file path.')
    try:
        if orig_path.split('.')[-1] == 'nson':
            await decode(orig_path)
        elif orig_path.split('.')[-1] == 'json':
            await encode(orig_path)
        else:
            raise Warning
    except FileExistsError:
        print(f'{path.dirname(orig_path)}/Edit_File.json already exists.')
    except FileNotFoundError:
        print(f'{orig_path} does not exist.')
    except IsADirectoryError:
        print(f'{orig_path} is a directory.')
    except PermissionError:
        print(f'Permission error, lack of read / write access.')
    except Warning:
        print(f'Wrong file format.  Expected : {".nson" if cmd =="-decode" else ".json"}')
    except Exception as ex:
        print(f'Exception type - {type(ex)}\tException args - {ex.args}\tException - {ex}')

async def async_read_file(filename, flags):
    async with open(filename, flags) as f:
        content = await f.read()
    return content

@pytest.mark.asyncio
async def test_integrity():
    orig_nson = await async_read_file('GameSave001.nson', 'rb')
    await decode('GameSave001.nson')
    await encode('Edit_File.json')
    new_nson = await async_read_file('Edited_Save_File.nson', 'rb')
    assert orig_nson == new_nson
