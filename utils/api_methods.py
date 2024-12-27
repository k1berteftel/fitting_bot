import asyncio
from PIL import Image
from aiohttp import ClientSession
import base64
from pathlib import Path
import json

api_key = 'fa-GWDyIiwJAxE4-f4I0gw42yOWHTkzW0NnQI2DT'


async def concatenate_images(cloth: str | Path, model: str | Path, category: str, **kwargs) -> list[str] | None:
    '''
    :param cloth: Ссылка на фотографию одежды или же его путь в рабочей директории
    :param model: Ссылка на фотографию модели или же его путь в рабочей директории
    :param category: название категории примерки
    :param kwargs: дополнительные параметры
    :return: list[str]
    Возвращает список сгенерированных картинок или же вызывает исключение в случае пропала
    '''

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print(model, cloth)
    url = 'https://api.fashn.ai/v1/run'
    if isinstance(model, Path):
        encoded = base64.b64encode(open(model, 'rb').read()).decode('utf-8')
        model = f'data:image/jpg;base64, {encoded}'
    if isinstance(cloth, Path):
        encoded = base64.b64encode(open(cloth, 'rb').read()).decode('utf-8')
        cloth = f'data:image/jpg;base64, {encoded}'
    params = {
        "model_image": model,
        "garment_image": cloth,
        "category": category
    }

    params.update(kwargs)
    print('start request')
    async with ClientSession() as session:
        async with session.post(url, headers=headers, json=params) as response:
            data = await response.json()
            if not data['id']:
                raise Exception(data['error'])
            id = data['id']
        while True:
            async with session.get(f'https://api.fashn.ai/v1/status/{id}', headers=headers) as response:
                data = await response.json()
                if data['status'] == 'completed':
                    result = data['output']
                    break
                if data['error']:
                    raise Exception(data['error'])
                if data['status'] == 'canceled':
                    return None
                await asyncio.sleep(2)
    return result
    # async with session.get(f'https://api.fashn.ai/v1/status/{id}', headers=headers) as response:


async def add_background(image: str, bg_image: str, user_id: int) -> str:
    url = 'https://api.acetone.ai/api/v1/remove/background?format=png'
    headers = {
        'Token': '62b37ad5-f91a-4212-9b14-31c549375e1e'
    }
    params = {
        'bg_mode': 'image'
    }
    files = {
        'image': open(image, 'rb').read(),
        'bgimage': open(bg_image, 'rb').read()
    }
    async with ClientSession() as session:
        async with session.post(url, headers=headers, params=params, data=files) as response:
            print(response)
            print(response.content)
            with open(f'{user_id}_output.png', 'wb') as file:
                file.write(await response.content.read())
    return f'{user_id}_output.png'



#asyncio.run(add_background('cloth_1236300146.jpg', 'model_1236300146.jpg'))



#asyncio.run(concatenate_images(Path('cloth_1236300146.jpg'), Path('model_1236300146.jpg'), 'tops'))


async def add_watermark(image: str, user_id: int) -> str:
    # Открываем основное изображение
    image = Image.open(image).convert("RGBA")
    image_width, image_height = image.size

    # Открываем изображение водяного знака
    watermark = Image.open('watermark.jpg').convert("RGBA")
    watermark_width, watermark_height = watermark.size

    # Масштабируем водяной знак (по ширине основного изображения)
    new_width = int(image_width * 0.35)
    new_height = int(new_width * watermark_height / watermark_width)
    watermark = watermark.resize((new_width, new_height))

    # Применяем прозрачность
    watermark = watermark.copy()
    alpha = watermark.split()[3]  # Канал альфа
    alpha = alpha.point(lambda p: p * (200 / 255.0))
    watermark.putalpha(alpha)

    # Позиция водяного знака (правый нижний угол)
    x = image_width - new_width - 10  # Отступ 10px
    y = image_height - new_height - 10

    # Создаём новый слой для объединения
    transparent_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
    transparent_layer.paste(watermark, (x, y), watermark)

    # Объединяем изображения
    watermarked_image = Image.alpha_composite(image, transparent_layer)

    # Сохраняем результат
    watermarked_image.convert("RGB").save(f'{user_id}.png', "JPEG")

    return f'{user_id}.png'


#asyncio.run(add_watermark('model_1236300146.jpg', 1236300146))
