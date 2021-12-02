import logging

from environs import Env
from terminaltables import DoubleTable

from parse_vacancies import parse_vacancies_hh, parse_sj_vacancies


logger = logging.getLogger('logger_main')


def predict_common_salary(salary_from, salary_to):
    if not (salary_from and salary_to):
        return None
    if not salary_from:
        return salary_to * 0.8
    elif not salary_to:
        return salary_from * 1.2
    return (salary_from + salary_to) / 2


def predict_rub_salary_hh(vacancy):
    if vacancy['salary']:
        if vacancy['salary']['currency'] == 'RUR':
            return predict_common_salary(
                vacancy['salary']['from'],
                vacancy['salary']['to'],
            )
    return None


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] != 'rub':
        return None
    return predict_common_salary(
        vacancy['payment_from'],
        vacancy['payment_to'],
    )


def fetch_all_rub_salary(vacancies, predict_rub_salary):
    all_salaries = []
    for vacancy in vacancies:
        vacancy_salary = predict_rub_salary(vacancy)
        if vacancy_salary:
            all_salaries.append(vacancy_salary)
    return all_salaries


def get_language_stat(all_salaries, found):
    average_salary = int(sum(all_salaries) / len(all_salaries))
    return {
        'vacancies_found': found,
        'vacancies_processed': len(all_salaries),
        'average_salary': average_salary
    }


def get_vacancies_statistic_hh(
            languages,
            hh_professional_roles,
            hh_parent_area,
            hh_area,
            hh_period
        ):
    vacancies_statistic = {}
    for language in languages:
        vacancies, found = parse_vacancies_hh(
            language,
            professional_roles=hh_professional_roles,
            parent_area=hh_parent_area,
            area=hh_area,
            period=hh_period,
        )
        all_salaries = fetch_all_rub_salary(vacancies, predict_rub_salary_hh)
        if not all_salaries:
            continue
        vacancies_statistic[language] = get_language_stat(all_salaries, found)
    return vacancies_statistic


def get_vacancies_statistic_sj(
            languages,
            sj_catalogues,
            sj_town,
            sj_secret_key
        ):
    vacancies_statistic = {}
    for language in languages:
        vacancies, found = parse_sj_vacancies(
            language,
            catalogues=sj_catalogues,
            town=sj_town,
            superjob_secret_key=sj_secret_key,
        )
        all_salaries = fetch_all_rub_salary(vacancies, predict_rub_salary_sj)
        if not all_salaries:
            continue
        vacancies_statistic[language] = get_language_stat(all_salaries, found)
    return vacancies_statistic


def draw_terminaltable(statistic, title):
    table_content = [
        [
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата'
        ],
    ]
    for language, statistic in statistic.items():
        table_line = [
            language,
            statistic['vacancies_found'],
            statistic['vacancies_processed'],
            statistic['average_salary'],
        ]
        table_content.append(table_line)

    table = DoubleTable(table_content, title)
    return table.table


def main():
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
    )
    logger.setLevel(logging.INFO)

    env = Env()
    env.read_env()
    languages = env.list(
        'LANGUAGES',
        [
            'JavaScript',
            'Java',
            'Python',
            'Ruby',
            'PHP',
            'C++',
            'C#',
            'Go',
            'TypeScript',
        ],
    )

    hh_professional_roles = env('HH_PROFESSIONAL_ROLE', '96')
    hh_parent_area = env('HH_PARENT_AREA', '113')
    hh_area = env('HH_AREA', '1')
    hh_period = env('HH_SEARCHING_PERIOD', '30')

    sj_catalogues = env('SJ_CATALOGUES_CODE', '48')
    sj_town = env('SJ_TOWN', '113')
    sj_secret_key = env('SUPERJOB_SECRET_KEY')

    vacancies_statistic_hh = get_vacancies_statistic_hh(
        languages,
        hh_professional_roles,
        hh_parent_area,
        hh_area,
        hh_period,
    )
    vacancies_statistic_sj = get_vacancies_statistic_sj(
        languages,
        sj_catalogues,
        sj_town,
        sj_secret_key,
    )

    print(draw_terminaltable(vacancies_statistic_hh, 'HeadHunter Moscow'))
    print(draw_terminaltable(vacancies_statistic_sj, 'SuperJob Moscow'))


if __name__ == '__main__':
    main()
