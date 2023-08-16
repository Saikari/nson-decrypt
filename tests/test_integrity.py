from zlib import compressobj, decompressobj
from os import path
from aiofiles import open as open_async
from asyncio import run
import pytest

async def async_decode(orig_path):
    byte_arr = await async_read_file(orig_path, 'rb')
    obj = decompressobj(wbits=-15)
    async with open_async('Edit_File.json', mode='wb') as write_file:
        await write_file.write(obj.decompress(byte_arr))
    print(f'Edit_File.json has been written to disk asynchronously.')


def sync_decode(orig_path):
    byte_arr = sync_read_file(orig_path, 'rb')
    obj = decompressobj(wbits=-15)
    with open('Edit_File.json', mode='wb') as write_file:
        write_file.write(obj.decompress(byte_arr))
    print(f'Edit_File.json has been written to disk synchronously.')

async def async_encode(new_path):
    save_data = await async_read_file(new_path, 'rb')
    obj = compressobj(wbits=-15)
    async with open_async('Edited_Save_File.nson', mode='wb') as new_save:
        await new_save.write(obj.compress(save_data))
    print(f'Edited_Save_File.nson has been written to disk asynchronously.')

def sync_encode(new_path):
    save_data = sync_read_file(new_path, 'rb')
    obj = compressobj(wbits=-15)
    with open('Edited_Save_File.nson', mode='wb') as new_save:
        new_save.write(obj.compress(save_data))
    print(f'Edited_Save_File.nson has been written to disk synchronously.')


async def cmdhandler(cmd):
    orig_path = input(f'Please enter {".nson" if cmd =="-decode" else ".json"} file path.')
    try:
        if orig_path.split('.')[-1] == 'nson':
            await async_decode(orig_path)
        elif orig_path.split('.')[-1] == 'json':
            await async_encode(orig_path)
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
    async with open_async(filename, flags) as f:
        content = await f.read()
    return content
def sync_read_file(filename, flags):
    with open(filename, flags) as f:
        content = f.read()
    return content


def test_integrity():
    print(sync_read_file('GameSave001.nson','rb'))
    sync_decode('GameSave001.nson')
    print(sync_read_file('Edit_File.json','r'))
    sync_encode('Edit_File.json')
    print(sync_read_file('Edited_Save_File.nson','rb'))
    assert sync_read_file('GameSave001.nson', 'rb') == sync_read_file('Edited_Save_File.nson', 'rb')
