from collections import defaultdict

from environs import Env
from terminaltables import DoubleTable

from parce_vacancies import parse_hh_vacancies, parce_sj_vacancies


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
    if not vacancy['currency'] != 'rub':
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


def get_vacancies_statistic(parce_source, predict_rub_salary, secret_key=None):
    vacancies_statistic = defaultdict(str)
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
        ]
    )
    for language in languages:
        vacancies, found = parce_source(language, secret_key)
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
    sj_secret_key = env('SUPERJOB_SECRET_KEY')

    vacancies_statistic_hh = get_vacancies_statistic(
        parse_hh_vacancies,
        predict_rub_salary_hh,
    )
    vacancies_statistic_sj = get_vacancies_statistic(
        parce_sj_vacancies,
        predict_rub_salary_sj,
        sj_secret_key
    )

    print(draw_terminaltable(vacancies_statistic_hh, 'HeadHunter Moscow'))
    print(draw_terminaltable(vacancies_statistic_sj, 'SuperJob Moscow'))


if __name__ == '__main__':
    env = Env()
    env.read_env()
    main()
