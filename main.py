import logging
from collections import defaultdict

from environs import Env
from terminaltables import DoubleTable

from parse_vacancies import parse_hh_vacancies, parse_sj_vacancies


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
    if vacancy['salary']['currency'] != 'RUR':
        return None
    return predict_common_salary(
        vacancy['salary']['from'],
        vacancy['salary']['to'],
    )


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


def get_vacancies_statistic(parse_source, predict_rub_salary, languages, api_parameters, secret_key=None):
    vacancies_statistic = defaultdict(str)
    for language in languages:
        vacancies, found = parse_source(api_parameters, language, secret_key)
        all_salaries = fetch_all_rub_salary(vacancies, predict_rub_salary)
        if not all_salaries:
            continue
        average_salary = int(sum(all_salaries) / len(all_salaries))
        vacancies_statistic[language] = {
            'vacancies_found': found,
            'vacancies_processed': len(all_salaries),
            'average_salary': average_salary
        }
    return vacancies_statistic


def draw_terminaltable(statistic, title):
    table_data = [
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
        table_data.append(table_line)

    table = DoubleTable(table_data, title)
    return table.table


def main():
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
    )
    logger.setLevel(logging.INFO)

    env = Env()
    env.read_env()
    LANGUAGES = env.list(
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

    HH_API_PARAMETERS = env.dict(
        'HH_API_PARAMETERS',
        {
            'programmer_role': '96',
            'moscow_parent_area': '113',
            'moscow_area': '1',
            'number_of_days': '30',
        },
        subcast_values=str,
    )
    vacancies_statistic_hh = get_vacancies_statistic(
        parse_hh_vacancies,
        predict_rub_salary_hh,
        languages=LANGUAGES,
        api_parameters=HH_API_PARAMETERS,
    )

    SUPERJOB_SECRET_KEY = env('SUPERJOB_SECRET_KEY')
    SJ_API_PARAMETERS = env.dict(
        'SJ_API_PARAMETERS',
        {
            'programmer_number': '48',
            'moscow_area': 'Москва',
        },
        subcast_values=str,
    )
    vacancies_statistic_sj = get_vacancies_statistic(
        parse_sj_vacancies,
        predict_rub_salary_sj,
        languages=LANGUAGES,
        secret_key=SUPERJOB_SECRET_KEY,
        api_parameters=SJ_API_PARAMETERS,
    )

    print(draw_terminaltable(vacancies_statistic_hh, 'HeadHunter Moscow'))
    print(draw_terminaltable(vacancies_statistic_sj, 'SuperJob Moscow'))


if __name__ == '__main__':
    main()
