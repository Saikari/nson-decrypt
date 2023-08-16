import zlib
import pathlib
import aiofiles
import hashlib
import pytest
import os

async def async_decode(original_path):
    async with aiofiles.open(original_path, mode='rb') as original_file:
        byte_arr = await original_file.read()
    obj = zlib.decompressobj(wbits=-15)
    async with aiofiles.open('Edit_File.json', mode='wb') as write_file:
        await write_file.write(obj.decompress(byte_arr))
    print(f'Edit_File.json has been written to disk asynchronously.')


def sync_decode(original_path):
    with open(original_path, mode='rb') as original_file:
        byte_arr = original_file.read()
    obj = zlib.decompressobj(wbits=-15)
    with open('Edit_File.json', mode='wb') as write_file:
        write_file.write(obj.decompress(byte_arr))
    print(f'Edit_File.json has been written to disk synchronously.')


async def async_encode(new_path):
    async with aiofiles.open(new_path, mode='rb') as new_file:
        save_data = await new_file.read()
    obj = zlib.compressobj(wbits=-15)
    async with aiofiles.open('Edited_Save_File.nson', mode='wb') as new_save:
        await new_save.write(obj.compress(save_data))
    print(f'Edited_Save_File.nson has been written to disk asynchronously.')


def sync_encode(new_path):
    with open(new_path, mode='rb') as new_file:
        save_data = new_file.read()
    obj = zlib.compressobj(wbits=-15)
    with open('Edited_Save_File.nson', mode='wb') as new_save:
        new_save.write(obj.compress(save_data))
        new_save.flush()
        new_save.close()
    print(f'Edited_Save_File.nson has been written to disk synchronously.')

    # Check if the file exists
    assert os.path.exists('Edited_Save_File.nson'), 'File not found'

    # Check if the file is not empty
    assert os.path.getsize('Edited_Save_File.nson') > 0, 'File is empty'

    # Check the content of the file
    with open('Edited_Save_File.nson', mode='rb') as edited_file:
        edited_content = edited_file.read()
    assert edited_content == obj.compress(save_data), 'File content does not match'



async def cmdhandler(cmd):
    file_extension = '.nson' if cmd == '-decode' else '.json'
    original_path = input(f'Please enter {file_extension} file path: ')
    try:
        if original_path.endswith('.nson'):
            await async_decode(original_path)
        elif original_path.endswith('.json'):
            await async_encode(original_path)
        else:
            raise Warning
    except FileExistsError:
        print(f'{pathlib.Path(original_path).parent}/Edit_File.json already exists.')
    except FileNotFoundError:
        print(f'{original_path} does not exist.')
    except IsADirectoryError:
        print(f'{original_path} is a directory.')
    except PermissionError:
        print(f'Permission error, lack of read / write access.')
    except Warning:
        print(f'Wrong file format. Expected: {file_extension}')
    except Exception as ex:
        print(f'Exception type - {type(ex)}\tException args - {ex.args}\tException - {ex}')


async def async_read_file(filename, flags):
    async with aiofiles.open(filename, flags) as f:
        content = await f.read()
    return content


def sync_read_file(filename, flags):
    with open(filename, flags) as f:
        content = f.read()
    return content


@pytest.fixture
def original_file_path():
    return 'GameSave001.nson'


@pytest.fixture
def edited_file_path():
    return 'Edited_Save_File.nson'


@pytest.fixture
def edited_json_path():
    return 'Edit_File.json'


def test_integrity(original_file_path, edited_file_path, edited_json_path):
    with open(original_file_path, 'rb') as original_file:
        original_content = original_file.read()
    sync_decode(original_file_path)
    with open(edited_json_path, 'r') as edited_json_file:
        edited_json_content = edited_json_file.read()
    sync_encode(edited_json_path)
    with open(edited_file_path, 'rb') as edited_file:
        edited_content = edited_file.read()
    assert edited_content == zlib.compress(original_content, wbits=-15), 'Edited content does not match original content'
    assert pathlib.Path(edited_json_path).exists(), 'Edited JSON file does not exist'
    assert pathlib.Path(edited_file_path).exists(), 'Edited file does not exist'
    assert edited_json_path.endswith('.json'), 'Edited JSON file has incorrect file extension'
    assert edited_file_path.endswith('.nson'), 'Edited file has incorrect file extension'
    assert pathlib.Path(original_file_path).stat().st_size == pathlib.Path(edited_file_path).stat().st_size, 'Original and edited files have different sizes'
    assert len(edited_content) < len(original_content), 'Compressed content of edited file is not smaller than original content'
    original_lines = original_content.decode().splitlines()
    edited_lines = edited_content.decode().splitlines()
    assert len(original_lines) == len(edited_lines), 'Original and edited files have different number of lines'
    assert pathlib.Path(edited_json_path).stat().st_mode == pathlib.Path(edited_file_path).stat().st_mode, 'Edited JSON file and edited file have different permissions'
    assert len(sync_read_file(edited_json_path, 'rb')) > 0, 'Edited JSON file is empty'
    assert len(sync_read_file(edited_file_path, 'rb')) > 0, 'Edited file is empty'
    assert hashlib.sha256(original_content).hexdigest() == hashlib.sha256(sync_read_file(edited_json_path, 'rb')).hexdigest(), 'Edited JSON file is corrupted'
    assert hashlib.sha256(original_content).hexdigest() == hashlib.sha256(edited_content).hexdigest(), 'Edited file is corrupted'
    assert 'assert' not in sync_read_file(__file__, 'r'), 'Code contains assert statements that should not be used in production environments'



