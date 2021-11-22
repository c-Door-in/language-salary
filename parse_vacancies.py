import logging
from itertools import count

import requests


logger = logging.getLogger('logger_main')


def parse_hh_vacancies(language, secret_key):
    url = 'https://api.hh.ru/vacancies'
    vacancies = []
    for page in count(0):
        params = {
                'professional_roles': '96',
                'text': language.lower(),
                'parent_area': '113',
                'area': '1',
                'period': '30',
                'page': page,
                'only_with_salary': 'true',
            }
        response = requests.get(url, params=params)
        response.raise_for_status()

        if page >= response.json()['pages']:
            break

        vacancies.extend(response.json()['items'])
        logger.info(
            'Page %s of %s was added successfully', page, language,
        )

    return vacancies, response.json()['found']


def parse_sj_vacancies(language, secret_key):
    url = 'https://api.superjob.ru/2.0/vacancies'
    vacancies = []
    headers = {
        'X-Api-App-Id': secret_key,
    }
    for page in count(0):
        params = {
            'catalogues': '48',
            'town': 'Москва',
            'no_agreement': '1',
            'page': page,
            'keyword': language.lower(),
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        vacancies.extend(response.json()['objects'])
        logger.info(
            'Page %s of %s was added successfully', page, language,
        )
        if not response.json()['more']:
            break

    return vacancies, response.json()['total']
