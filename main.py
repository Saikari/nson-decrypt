from zlib import compressobj, decompressobj
from os import path
from aiofiles import open
from asyncio import run
from re import sub


async def decode(orig_path):
    async with open(orig_path, mode='rb') as save_file:
        byte_arr = await save_file.read()
    obj = decompressobj(wbits=-15)
    async with open(f'{path.dirname(orig_path)}/Edit_File.json', mode='wb') as write_file:
        data = obj.decompress(byte_arr)
        await write_file.write(data)
    text = sub(r'\\{3}"(.*?)\\{3}', r'"\1', data.decode('UTF-8'))
    text = sub(r'\\{2}"(.*?)\\{2}"', r'"\1"', text)
    text = sub(r'\["{', '[{', text)
    text = sub(r']}"', ']}', text)
    text = sub(r'"{(.*?)}"', r'{\1}', text)
    print(sub(r'\\"(.*?)\\"', r'"\1"', text))
    print(f'{path.dirname(orig_path)}/Edited_Save_File.nson has been written to disk.')


async def encode(new_path):
    async with open(new_path, mode='rb') as edit_file:
        save_data = await edit_file.read()
    obj = compressobj(wbits=-15)
    async with open(f'{path.dirname(new_path)}/Edited_Save_File.nson', mode='wb') as new_save:
        await new_save.write(obj.compress(save_data))
    print(f'{path.dirname(new_path)}/Edited_Save_File.nson has been written to disk.')


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


async def main():
    while True:
        cmd = input('Please input command : -encode\t-decode\t-exit\n')
        match cmd:
            case '-encode':
                await cmdhandler(cmd)
            case '-decode':
                await cmdhandler(cmd)
            case '-exit':
                break


run(main())
