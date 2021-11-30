import logging
from itertools import count

import requests


logger = logging.getLogger('logger_main')


def parse_vacancies_hh(language, professional_roles, parent_area, area, period):
    url = 'https://api.hh.ru/vacancies'
    vacancies = []
    for page in count(0):
        params = {
                'professional_roles': professional_roles,
                'text': language.lower(),
                'parent_area': parent_area,
                'area': area,
                'period': period,
                'page': page,
                'only_with_salary': 'true',
            }
        response = requests.get(url, params=params)
        response.raise_for_status()

        hh_vacancies_summary = response.json()

        if page >= hh_vacancies_summary['pages']:
            break

        vacancies.extend(hh_vacancies_summary['items'])
        logger.info(
            'Page %s of %s was added successfully', page, language,
        )

    return vacancies, hh_vacancies_summary['found']


def parse_sj_vacancies(language, catalogues, town, superjob_secret_key):
    url = 'https://api.superjob.ru/2.0/vacancies'
    vacancies = []
    headers = {
        'X-Api-App-Id': superjob_secret_key,
    }
    for page in count(0):
        params = {
            'catalogues': catalogues,
            'town': town,
            'no_agreement': '1',
            'page': page,
            'keyword': language.lower(),
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        sj_vacancies_summary = response.json()

        vacancies.extend(sj_vacancies_summary['objects'])
        logger.info(
            'Page %s of %s was added successfully', page, language,
        )
        if not sj_vacancies_summary['more']:
            break

    return vacancies, sj_vacancies_summary['total']
