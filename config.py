from os import getenv

db_url = getenv('DATABASE_URL')

# Настройки для телеграма
tg_link = 'https://t.me/itsolschool_heizenberg_bot'
tg_token = getenv('TG_TOKEN')

# Настройки для ВК
vk_link = 'https://vk.com/im?sel=-174147611'
vk_token = getenv('VK_TOKEN')
vk_domain_verify_salt = getenv('VK_VERIFY_SALT')
