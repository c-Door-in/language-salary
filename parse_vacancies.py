import logging
from itertools import count

import requests


logger = logging.getLogger('logger_main')


def parse_vacancies_hh(language, professional_roles, parent_area, area, period):
    vacancies = []
    url = 'https://api.hh.ru/vacancies'
    params = {
        'professional_roles': professional_roles,
        'text': language.lower(),
        'parent_area': parent_area,
        'area': area,
        'period': period,
    }
    for page in count(0):
        params['page'] = page
        response = requests.get(url, params=params)
        response.raise_for_status()

        vacancies_summary = response.json()
        vacancies.extend(vacancies_summary['items'])
        logger.info(
            'Page %s of %s was added successfully', page, language,
        )
        if page == vacancies_summary['pages'] - 1:
            break

    return vacancies, vacancies_summary['found']


def parse_sj_vacancies(language, catalogues, town, superjob_secret_key):
    vacancies = []
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers = {'X-Api-App-Id': superjob_secret_key}
    params = {
        'catalogues': catalogues,
        'town': town,
        'keyword': language.lower(),
    }
    for page in count(0):
        params['page'] = page
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        vacancies_summary = response.json()

        vacancies.extend(vacancies_summary['objects'])
        logger.info(
            'Page %s of %s was added successfully', page, language,
        )
        if not vacancies_summary['more']:
            break

    return vacancies, vacancies_summary['total']
