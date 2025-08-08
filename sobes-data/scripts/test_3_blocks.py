import requests
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_3_blocks():
    PROXY_API_KEY = "sk-yseNQGJXYUnn4YjrnwNJnwW7bsnwFg8K"

    prompt_template = """Ты - эксперт по анализу IT-собеседований. Извлеки ВСЕ отдельные вопросы и задачи из текста интервью.

ИЗВЛЕКАЙ ПОЛНЫЕ формулировки задач, но:
- ПРОПУСКАЙ неинформативные ссылки ("отсюда", "с того собеса")
- ОБЪЕДИНЯЙ фрагменты в цельные задачи  
- СОХРАНЯЙ технические детали и требования
- НЕ извлекай бессмысленные обрывки ("Иначе false", "Возвращает данные")
- ИЗВЛЕКАЙ даже короткие, но осмысленные вопросы ("event-loop", "Что такое замыкания")

КРИТИЧЕСКИ ВАЖНО:
- Каждый вопрос = отдельная строка
- Каждая задача = отдельная строка  
- НЕ РАЗБИВАЙ одну задачу на части! Если по смыслу это одна задача - делай ОДНУ строку
- Каждая строка должна иметь СМЫСЛ как отдельный вопрос/задача
- НЕ создавай бессмысленные фрагменты
- Определи компанию из текста
- Извлеки дату из текста в формате YYYY-MM-DD
- Используй interview_id: {interview_id} для группировки всех вопросов из этого собеседования
- Возвращай ТОЛЬКО чистый CSV БЕЗ ```csv``` блоков и БЕЗ заголовка

CSV ФОРМАТ:
id,question_text,company,date,interview_id

ПРАВИЛЬНЫЕ ПРИМЕРЫ:
q1,"Реализуйте функцию debounce с настраиваемой задержкой",Яндекс,2025-07-18,interview_001
q2,"Promise задача: определить что выводится в консоль при обработке асинхронного кода",Яндекс,2025-07-18,interview_001
q3,"Задача на замыкание: написать функцию runOnce которая выполняется только один раз",Сбер,2025-07-17,interview_002
q4,"event-loop",Яндекс,2025-07-14,interview_003

НЕПРАВИЛЬНЫЕ ПРИМЕРЫ (НЕ ДЕЛАЙ ТАК):
q1,"Необходимо написать функцию",Яндекс,2025-07-17,interview_001
q2,"которая на вход принимает url",Яндекс,2025-07-17,interview_001  
q3,"Иначе false",Яндекс,2025-07-17,interview_001
И подобные примеры, где нет смысла в вопросе или он не является отдельной задачей


ОБРАБОТАЙ:
{full_content}"""

    # 3 БЛОКА ИЗ ТВОЕГО ВЫДЕЛЕНИЯ
    blocks = [
        # БЛОК 1 - Арчим с комплексными задачами 
        """2025-07-07 15:36:45
 Fetisov Artem -> 2071074234:
1. Яндекс 1 этап
HR сама написала(сказала что ищут фронта в Яндекс Маркет)
ЗП 300к


1. Сделать обертку над функцией, чтобы она вызывалась один раз. Все последующие вызовы должны вернуть undefined.
function runOnce(fn) {
  let isCalled = false;
  return (...args) => {
    if (isCalled) {
      return undefined; // уже вызывалась — ничего не делаем
    }
    isCalled = true;
    return fn(...args); // вызываем fn только один раз
  };
}

2. Написать функцию которая спит определенное время а затем возвращает значение.
function sleep(duration) {
  // Возвращаем новый промис
  return new Promise(resolve => {
    // Используем setTimeout для задержки
    setTimeout(() => {
      // После завершения задержки, вызываем resolve промиса
      resolve()
    }, duration)
  })
}

3. Необходимо реализовать метод groupBy, расширяющий стандартные методы массивов. Метод должен возвращать сгруппированную версию массива — объект, в котором каждый ключ является результатом выполнения переданной функции fn(arr[i]), а каждое значение — массивом, содержащим все элементы исходного массива с этим ключом.
Array.prototype.groupBy = function (fn) {
  return this.reduce((result, item) => {
    const key = fn(item) // Вычисляем ключ для текущего элемента
    if (!result[key]) {
      // Если такого ключа ещё нет в объекте
      result[key] = [] // Создаём пустой массив для этого ключа
    }
    result[key].push(item) // Добавляем элемент в соответствующую группу
    return result
  }, {}) // Начинаем с пустого объекта
}


4. Необходимо проверить решение задачи по двум сервисам, вызвав checkResult(url1, solution), checkResult(url2, solution)
checkResult: (url: string, solution: string | number) => Promise<boolean>;
* Если оба запроса вернули true - вывести succes
* Если хоть один вернул false - вывести fail
* Если хоть зареджектился - вывести error
* Если хоть один отвечает дольше 1 сек - вывести timeout
import { checkResult } from 'myLib'

const solution = 'Any answer'
const url1 = 'yandex.ru'
const url2 = 'google.com'

checkResult(url, solution)
checkResult(url, solution)

async function check() {
  const TIMEOUT_MS = 1000

  // Оборачиваем каждый вызов в Promise.race с таймаутом
  const withTimeout = url => {
    return Promise.race([
      checkResult(url, solution), // основной вызов
      new Promise(
        (
          _,
          reject // таймаут
        ) => setTimeout(() => reject(new Error('timeout')), TIMEOUT_MS)
      ),
    ])
  }

  try {
    // Запускаем оба запроса параллельно
    const [res1, res2] = await Promise.all([
      withTimeout(url1),
      withTimeout(url2),
    ])

    // Если оба true
    if (res1 === true && res2 === true) {
      console.log('success')
    }
    // Если хотя бы один false
    else if (res1 === false || res2 === false) {
      console.log('fail')
    }
  } catch (err) {
    // Если ошибка — различаем таймаут и другую ошибку
    if (err.message === 'timeout') {
      console.log('timeout')
    } else {
      console.log('error')
    }
  }
}

check()

5. У вас есть два пользователя, у каждого из которых записаны интервалы времени, когда они были свободны. Эти интервалы представлены в виде массива пар [start, end], где start - начало интервала, end - конец интервала. Интервалы у каждого пользователя отсортированы в порядке возрастания и не пересекаются между собой. Напишите функцию intersection(user1, user2), которая находит все интервалы времени, когда оба пользователя были свободны одновременно.
function intersection(user1, user2) {
  let i = 0;
  let j = 0;
  const result = [];

  while (i < user1.length && j < user2.length) {
    const [start1, end1] = user1[i];
    const [start2, end2] = user2[j];

    // вычисляем пересечение
    const start = Math.max(start1, start2);
    const end = Math.min(end1, end2);

    if (start < end) {
      result.push([start, end]);
    }

    // двигаем указатель в том массиве, у которого текущий интервал раньше заканчивается
    if (end1 < end2) {
      i++;
    } else {
      j++;
    }
  }

  return result;
}""",

        # БЛОК 2 - Никита с системными задачами
        """2025-07-07 12:45:39
 Никита -> 2071074234:
Яндекс 2 этап
ЗП: от 240

Задача 1:
/*
interface Message {
    id: number
    text: string
}

Id самого первого сообщения = 1, а id каждого следующего сообщения на 1 больше, чем id предыдущего.
Нам нужно выводить сообщения в правильном порядке, однако сервер не гарантирует правильный порядок
сообщений, отправляемых в наше приложение.

Таймлайн:
(приходит) 7 1 2 3 6 5 4    8
(рисунок)   . 1 2 3 . . 4 5 6 7 8

Сообщения от сервера приходят в обработчик функции connect:

connect((msg) => {
    ...
});

Отображать сообщения нужно с помощью функции `render`:
render(msg)
*/

const solution = (connect, render) => {};
function solution(connect, render) {
  const map = new Map();  // Храним сообщения по id
  let currId = 1;

  connect((msg) => {
    map.set(msg.id, msg); // Просто сохраняем сообщение по id

    // Пока есть сообщение с ожидаемым id — рендерим и двигаемся дальше
    while (map.has(currId)) {
      const messageToRender = map.get(currId);
      render(messageToRender); // Вызываем render прямо сейчас
      map.delete(currId);      // Удаляем отрисованное сообщение
      currId++;
    }
  });
}

Задача 2
Не решил (Решение из базы)
//Дан массив ссылок: ['url1', 'url2', ...] и лимит одновременных запросов (limit) Необходимо реализовать функцию, которыя опросит урлы в том //порядку, в котором они идут в массиве, и вызовет callback с массивом ответов ['url1_answer', 'url2_anser', ...] так, чтобы в любой момент //времени выполнялось не более limit запросов (как только любой из них завершился, сразу же отправится следующий) Т.е. нужно реализовать шину с шириной равной limit.
// доп. добавить мемоизацию
function parallelLimit(urls, limit, callback) {
    // Если limit больше количества URL, устанавливаем его равным длине массива URL
    limit = Math.min(limit, urls.length);
    
    let results = new Array(urls.length);
    let active = 0;
    let index = 0;
    const cache = new Map(); // Добавляем кэш для мемоизации
    
    function processNext() {
        if (index >= urls.length && active === 0) {
            callback(results);
            return;
        }
        
        while (index < urls.length && active < limit) {
            const currIndex = index;
            const url = urls[currIndex];
            index++;
            active++;
            
            // Проверяем наличие URL в кэше
            if (cache.has(url)) {
                // Если URL уже в кэше, берём результат оттуда
                results[currIndex] = cache.get(url);
                active--;
                // Используем setTimeout для асинхронности и предотвращения переполнения стека
                setTimeout(processNext, 0);
            } else {
                // Если URL нет в кэше, выполняем запрос
                fetch(url)
                    .then(response => {
                        // Сохраняем ответ в кэш
                        cache.set(url, response);
                        results[currIndex] = response;
                        active--;
                        processNext();
                    });
            }
        }
    }
    
    // Обработка пустого массива URL
    if (urls.length === 0) {
        callback(results);
        return;
    }
    
    processNext();
}""",

        # БЛОК 3 - Иван с алгоритмами
        """2025-07-07 09:38:13
 Ivan -> 2071074234:
Название компании: Яндекс 07.07
ЗП: 300

Секция алгоритмических задач

Был душный интервьюер. Часто цепляется к словам и деталям решения почему именно так, а не иначе. Лучше говорить только то в чем уверен и рассуждать вслух аккуратно, чтоб не давать повода зацепиться.

1. Легенда задачи:  есть чат с сообщениями, сообщения могут приходить от сервера в произвольном порядке (проблема race condition). 
пример сообщения {id: 1, text: 'lorem ipsum'}
Кейс: если сообщения пришли от сервера в порядке 1-2-3-6-4-5, то в чате они все равно должны оказаться 1-2-3-4-5-6. (6 не отобразится пока не придет 5)
function solution(connect, render) {
    // Храним сообщения в Map, где ключ - id сообщения, значение - само сообщение
    const messages = new Map();
    // Ожидаем сообщение с этим id следующим
    let nextExpectedId = 1;

    connect(function onMessage(message) {
        // Добавляем сообщение в Map
        messages.set(message.id, message);

        // Пока есть ожидаемое сообщение, рендерим его и увеличиваем nextExpectedId
        while (messages.has(nextExpectedId)) {
            render(messages.get(nextExpectedId));
            messages.delete(nextExpectedId);
            nextExpectedId++;
        }
    });
}
2. Нужно сделать обход дерева без использования рекурсии. Дерево представляет собой структуру папок {name: '', childrens[]}
Нужно вывести структуру в консоль в красивом виде, чтоб количество пробелов соответствовало вложенности папки.
const stack = [{data, level: 0}]

while (stack.length > 0) {
  // Извлекаем текущий элемент из стека
  const { data, level } = stack.pop();
  console.log(" ".repeat(level*2) + data.name)
  // Если есть дети, добавляем их в стек в обратном порядке
  if (data.children && Array.isArray(data.children)) {
    for (let i = data.children.length - 1; i >= 0; i--) {
      stack.push({
        data: data.children[i],
        level: level + 1,
      });
    }
  }
}"""
    ]

    headers = {
        "Authorization": f"Bearer {PROXY_API_KEY}",
        "Content-Type": "application/json"
    }

    all_results = []

    print("ОБРАБОТКА 3 БЛОКОВ:")

    for i, block in enumerate(blocks, 1):
        print(f"\n{'='*50}")
        print(f"БЛОК {i}")
        print(f"{'='*50}")

        interview_id = f"interview_{i:03d}"
        prompt = prompt_template.format(full_content=block, interview_id=interview_id)

        payload = {
            "model": "gpt-4.1-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 2000
        }

        try:
            response = requests.post(
                "https://api.proxyapi.ru/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                csv_content = result['choices'][0]['message']['content'].strip()

                print(f"РЕЗУЛЬТАТ:")
                print(csv_content)

                # Добавляем к общим результатам
                lines = [line.strip() for line in csv_content.split('\n') if line.strip()]
                all_results.extend(lines)

                print(f"Извлечено {len(lines)} строк")
            else:
                print(f"Ошибка: {response.status_code}")

        except Exception as e:
            print(f"Ошибка: {str(e)}")

        if i < len(blocks):
            print("Пауза 3 секунды...")
            time.sleep(3)

    # Сохраняем итоговый результат
    print(f"\n{'='*50}")
    print("ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"{'='*50}")

    with open("final_3_blocks.csv", 'w', encoding='utf-8') as f:
        f.write("id,question_text,company,date,interview_id\n")
        for line in all_results:
            f.write(line + '\n')

    print(f"Всего извлечено: {len(all_results)} строк")
    print("Сохранено в final_3_blocks.csv")

if __name__ == "__main__":
    test_3_blocks()
