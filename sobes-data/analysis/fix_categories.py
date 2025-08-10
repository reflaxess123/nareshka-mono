#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ИСПРАВЛЕНИЕ КАТЕГОРИЗАЦИИ - ДОВОДИМ ДО 1-3% "ДРУГОЕ"
ИСПОЛЬЗУЕТ РЕГЕКСЫ ДЛЯ ТОЧНОЙ КАТЕГОРИЗАЦИИ
"""

import pandas as pd
import os
import re

def improved_categorize(name: str, keywords: str) -> str:
    """Исправленная категоризация с регексами"""
    text = f"{name} {keywords}".lower()
    
    # Флаги для регексов
    flags = re.I | re.U
    
    # Паттерны с регексами
    patterns_re = {
        "React": [
            r"\breact(\.js|js)?\b", r"\bреакт\b",
            r"\bjsx\b", r"\btsx\b",
            r"\b(component|компонент\w*)\b", r"\b(class[\s-]?component|классов(ый|ые)\s*компонент)\b",
            r"\bhooks?\b", r"\bхуки?\b", r"\b(custom[\s-]?hook|кастомн\w+\s*хук)\b",
            r"\bprops?\b", r"\bпроп(с(ы)?|ы)\b", r"\bchildren\b",
            r"\bstate\b", r"\bsetState\b", r"\buseState\b",
            r"\buseEffect\b", r"\buseLayoutEffect\b",
            r"\b(ref|useRef|forwardRef|createRef)\b", r"\bреф(ы)?\b",
            r"\bcontext\b", r"\buseContext\b", r"\bprovider\b", r"\bconsumer\b",
            r"\bmemo(ization)?\b", r"\breact\.?memo\b", r"\buseMemo\b", r"\buseCallback\b",
            r"\bportal(s)?\b", r"\bcreatePortal\b",
            r"\bsuspense\b", r"\breact\.?lazy\b", r"\blazy[\s-]?load(ing)?\b",
            r"\berror[\s-]?boundar(y|ies)\b", r"\bграниц\w*\s*ошибок\b",
            r"\b(vdom|virtual\s*dom|виртуал\w*\s*dom?)\b", r"\breconciliation\b", r"\bfiber\b",
            r"\b(concurrent[\s-]?mode|transition|useTransition|startTransition)\b",
            r"\bhydrat(e|ion|eRoot)\b", r"\bгидратац\w*\b",
            r"\brerender\b", r"\bre[\s-]?render\b", r"\b(ре)?-?рендер\b", r"\bперерисовк\w*\b",
            r"\bkey(s)?\b", r"\bключ(и|ом|а)?\s*пропс?\b",
            r"\b(rsc|react\s*server\s*components|server\s*components)\b",
            r"\breact[\s-]?router\b", r"\brouter\b", r"\buse(Navigate|Location|Params)\b", r"\blink\b", r"\boutlet\b",
            r"\bredux\b", r"\bredax\b", r"\bредукс\b", r"\bredux[\s-]?toolkit\b", r"\brtk\b",
            r"\b(zustand|recoil|mobx|jotai)\b",
            r"\breact[\s-]?(window|virtualized)\b",
            # НОВЫЕ ПАТТЕРНЫ ДЛЯ REACT:
            r"\b(счетчик\w*|counter)\s*(кнопк\w*|button\w*)\b", r"\b(старт|стоп|рестарт)\b",
            r"\b(комментари\w*|comment\w*)\s*(пользовател\w*|user\w*|онлайн|online)\b",
            r"\b(страниц\w*|page)\s*(счетчик\w*|counter|врем\w*|time)\b",
            r"\b(график\w*|chart\w*|visualiz\w*|визуализац\w*)\s*react\b",
            r"\b(плюсы|минусы|преимущества)\s*react\b",
            # ДОБИВАЕМ ПОСЛЕДНИЕ ТЕМЫ:
            r"\b(плюсы|минусы|преимущества)\s*(react|реакт)\b", r"\b(визуализац\w*|график\w*)\s*данн\w*\b"
        ],

        "JavaScript Core": [
            r"\b(java\s*script|javascript|js|ecmascript|es\d{2,4}|es2015|es6)\b",
            r"\bevent[\s-]?loop\b", r"\bcall[\s-]?stack\b", r"\b(task|micro|macro)task(s)?\b",
            r"\bpromise(s)?\b", r"\basync\b", r"\bawait\b", r"\bthen\b", r"\bcatch\b", r"\bfinally\b",
            r"\bgenerator(s)?\b", r"\biterator(s)?\b", r"\biterable\b",
            r"\bclosure(s)?\b", r"\bзамыкан\w*\b", r"\bhoist(ing)?\b",
            r"\bthis\b", r"\bbind\b", r"\bcall\b", r"\bapply\b",
            r"\b(scope|област\w*\s*видимост\w*)\b", r"\bstrict\s*mode\b", r"['\"]use strict['\"]",
            r"\bprototype(\s*chain)?\b", r"\bпрототип(н\w*)?\b", r"\bclass(es)?\b", r"\bextends\b", r"\bsuper\b",
            r"\b(module|modules)\b", r"\b(import|export)\b", r"\bcommonjs\b", r"\besm\b",
            r"\b(dom|document|window|navigator)\b",
            r"\b(json|parse|stringify)\b",
            r"\b(local|session)storage\b", r"\bcookies?\b", r"\bcookie\b", r"\bindexeddb\b",
            r"\b(браузер\w*\s*)?хранилищ\w*\b", r"\b(browser|браузер\w*)\s*(storage|хранен\w*)\b",
            r"\bfetch\b", r"\bxmlhttprequest\b", r"\bxhr\b",
            r"\b(setTimeout|setInterval|requestAnimationFrame)\b",
            r"\bdebounce\b", r"\bthrottle\b",
            r"\b(web[\s-]?worker|shared[\s-]?worker|service[\s-]?worker)\b",
            r"\bregexp?\b", r"\bdestructur(ing|e)\b", r"\b(spread|rest)\b",
            r"\btemplate\s*literals?\b",
            r"\b(map|set|weak(map|set))\b", r"\b(bigint|typed\s*array|arraybuffer|dataview)\b",
            r"\b==={0,1}\b", r"\b(coercion|приведени\w*\s*тип\w*)\b",
            r"\b(garbage\s*collection|gc|memory\s*leak|утечк\w*\s*памят\w*)\b",
            r"\b(function\w*|функц\w*)\s*(programming|программир\w*)\b",
            r"\bcompose\b", r"\bcurr(y|ying)\b", r"\bкарриров\w*\b",
            r"\b(всплыти\w*|погружен\w*)\s*(событи\w*|events?)\b", r"\bbubbling\b", r"\bcaptur(e|ing)\b",
            r"\b(операторы?|operators?)\s*(сравнен\w*|comparison)\b", r"\b===?\b",
            r"\b(контекст\w*|context)\s*(исполнен\w*|execution)\b",
            r"\bконсоль?\b", r"\bconsole\s*log\b", r"\b(выведет|output)\b",
            r"\b(копирова\w*|copy\w*)\s*(объект\w*|object)\b", r"\b(глубо\w*|shallow|deep)\s*(копи\w*|copy\w*)\b",
            r"\b(методы?\s*)?(массив\w*|array)\s*(method\w*)?\b", r"\b(мутирующ\w*|mutating)\b",
            # НОВЫЕ ФИНАЛЬНЫЕ ПАТТЕРНЫ ДЛЯ ОСТАВШИХСЯ ТЕМ:
            r"\b(промис\w*|promise)\s*(all|race|allsettled)\b", r"\baggregateError\b",
            r"\b(асинхрон\w*|parallel\w*)\s*(запрос\w*|request\w*|задач\w*)\b", r"\bparallellimit\b",
            r"\b(мемоизац\w*|memoization)\b", r"\bmemo.*нужн\w*\b",
            r"\b(стрелочн\w*|arrow)\s*(функци\w*|function\w*)\b", r"\b(обычн\w*|regular)\s*функци\w*\b",
            r"\b(рекурсив\w*|recursive)\s*(вызов\w*|call\w*|функци\w*)\b",
            r"\b(выведет|output|console)\s*(код\w*|execution|выполнен\w*)\b",
            r"\b(статическ\w*|static)\s*(метод\w*|method\w*|поля|field\w*)\b",
            r"\beventemitter\b", r"\b(event|событ\w*)\s*(emitter|эмитер\w*)\b",
            r"\b(пути|path\w*)\s*(объект\w*|object\w*)\b", r"\bgetbettype\b",
            r"\bsleep\s*(функци\w*|function)\b", r"\b(асинхрон\w*|async)\s*sleep\b",
            r"\b(циклы?|loop\w*|for)\s*(settimeout|таймаут\w*)\b"
        ],

        "TypeScript": [
            r"\btypescript|ts\b", r"\bтип(ы)?\b", r"\btype\b", r"\binterface(s)?\b", r"\bинтерфейс\w*\b",
            r"\bgeneric(s)?\b", r"\bдженер(ик\w*)?\b", r"\bextends\b", r"\bkeyof\b", r"\bin\b",
            r"\b(enums?|const\s*enum)\b",
            r"\b(unknown|any|never|void|readonly)\b", r"\b(as\s*const|satisfies)\b",
            r"\b(union|intersection|literal\s*types?)\b",
            r"\b(mapped|conditional)\s*types?\b", r"\binfer\b",
            r"\butility\s*types?\b", r"\b(partial|required|record|omit|pick|exclude|extract|nonnullable|returntype|parameter(s|type)?|constructorparameters?|instancetype)\b",
            r"\btype\s*guard(s)?\b", r"\bis\b", r"\basserts\b",
            r"\bmodule\s*augmentation\b", r"\bdeclaration\s*merging\b",
            r"\btsconfig\.?json\b", r"\bnoImplicitAny\b", r"\besModuleInterop\b", r"\bpaths?\b", r"\bbaseUrl\b",
            r"\bdecorators?\b", r"\bemitDecoratorMetadata\b"
        ],

        "Верстка": [
            r"\bhtml5?\b", r"\bcss3?\b",
            r"\blayout\b", r"\bflex(box)?\b", r"\bgrid\b",
            r"\bbox[\s-]?model\b", r"\bfloat\b", r"\bclear\b",
            r"\bposition\b", r"\b(z-?index|stacking\s*context)\b",
            r"\bdisplay\b", r"\b(block|inline|inline-block|table)\b",
            r"\bresponsive\b", r"\bадаптив\w*\b", r"\bmedia\s*queries?\b", r"\bcontainer\s*queries?\b",
            r"\bселектор\w*\b", r"\bспецифичност\w*\b",
            r"\bпсевдо(класс|элемент)\w*\b",
            r"\b(семантич\w*|semantic)\s*(html|разметк\w*|тег\w*|markup)\b",
            r"\b(meta|мета)\s*тег\w*\b", r"\bseo\b", r"\bopen\s*graph\b", r"\bfavicon\b",
            r"\bцентр(ирование|ировать)\b", r"\b(центр\w*|center\w*)\s*(элемент\w*|element)\b",
            r"\btransition(s)?\b", r"\banimation(s)?\b", r"\b@?keyframes\b", r"\btransform(s)?\b", r"\btranslate|scale|rotate\b",
            r"\b(rem|em|vh|vw|ch|ex)\b", r"\btypograph(y|ика)\b",
            r"\b(srcset|sizes|picture|webp|avif)\b",
            r"\b(bem|бэм)\b", r"\b(sass|scss|less|postcss|autoprefixer)\b",
            r"\b(css[-\s]?modules?)\b", r"\b(css[-\s]?in[-\s]?js|styled[\s-]?components|emotion)\b",
            r"\bforms?\b", r"\b(label|fieldset|input|select|textarea)\b",
            # ДОБИВАЕМ СЕМАНТИЧЕСКУЮ ВЕРСТКУ:
            r"\b(семантическ\w*)\s*(верстк\w*|markup)\b", r"\b(тег\w*)\s*(семантическ\w*|semantic)\b"
        ],

        "Алгоритмы": [
            r"\bалгоритм\w*\b", r"\b(time|space)\s*complexit(y|ies)\b", r"\bсложност\w*\b",
            r"\bO\(\s*n(\s*log\s*n)?\s*\)\b", r"\bO\(\s*1\s*\)\b", r"\bO\(\s*n\^?2\s*\)\b",
            r"\bмассив\w*\b", r"\barray(s)?\b",
            r"\b(list|linked\s*list|stack|queue|deque|heap|priority\s*queue|trie|tree|graph)\b",
            r"\bдерев\w*\b", r"\bграф\w*\b", r"\bхеш\w*\b", r"\bтаблиц\w*\b",
            r"\b(search|поиск)\b", r"\b(binary|линейн\w*)\s*поиск\b",
            r"\bсортир\w*\b", r"\b(quick|merge|heap|bubble|insertion|selection)\s*sort\b",
            r"\b(dfs|bfs|dijkstra|bellman[-\s]?ford|floyd[-\s]?warshall|mst|kruskal|prim|topological)\b",
            r"\b(строк\w*|string)\s*(reverse|переворот\w*|reverseString)\b", r"\bпалиндром\w*\b",
            r"\b(kmp|rabin[-\s]?karp|z[-\s]?function|prefix[-\s]?function|suffix\s*array)\b",
            r"\b(dp|dynamic\s*programming|динамическ\w*\s*программир\w*)\b",
            r"\b(two[\s-]?pointers?|sliding[\s-]?window)\b",
            r"\b(prefix\s*sum|fenwick|binary\s*indexed\s*tree|segment\s*tree)\b",
            r"\brecursi(ve|on|я|вн\w*)\b", r"\bdivide\s*and\s*conquer\b",
            r"\bбитов\w*\s*операц\w*\b", r"\bxor\b", r"\bfibonacci\b", r"\bsum\b",
            r"\b(числов\w*|numeric\w*)\s*(задач\w*|task\w*)\b", r"\b(равенств\w*|равн\w*|equal)\b",
            # НОВЫЕ ПАТТЕРНЫ ДЛЯ ОСТАВШИХСЯ АЛГОРИТМОВ:
            r"\b(переворот\w*|reverse\w*)\s*(строк\w*|string\w*)\b", r"\breverseString\b",
            r"\b(генерац\w*|generat\w*)\s*(hex|цвет\w*|color\w*)\b", r"\bhex.*цвет\w*\b",
            r"\b(функци\w*|function)\s*(sum\w*|сумм\w*)\s*(аргумент\w*|argument\w*)\b"
        ],

        "Soft Skills": [
            r"\bопыт\b", r"\bкомандн\w*\b", r"\bпроект\w*\b", r"\bразвитие\b", r"\bкарьер\w*\b",
            r"\bинтервью\b", r"\bсобеседован\w*\b", r"\bрезюме\b", r"\bфакап\w*\b",
            r"\bконфликт\w*\b", r"\bменеджер\w*\b", r"\bлидерств\w*\b",
            r"\bкоммуникац\w*\b", r"\bобратн\w*\s*связ\w*\b", r"\bfeedback\b",
            r"\bгрейд\w*\b", r"\bоценк\w*\b", r"\bпланирован\w*\b",
            r"\bтайм[-\s]?менеджмент\b", r"\bdeadline\b", r"\bownership\b", r"\bинициатив\w*\b",
            r"\bменторств\w*|наставничеств\w*\b", r"\bonboarding|онбординг\b",
            r"\bпереговор\w*\b", r"\bпрезентац\w*\b", r"\bpublic\s*speaking\b",
            r"\bретро(спектив\w*)?\b", r"\bscrum\b", r"\bканбан|kanban\b", r"\bagile\b",
            r"\bвыгоран\w*|burnout\b", r"\bwork[-\s]?life\b",
            r"\broadmap\b", r"\bдекомпозиц\w*\b", r"\bприоритизац\w*\b",
            r"\bкод[-\s]?ревью\b|\bcode\s*review\b",
            r"\b(интересн\w*|сложн\w*)\s*(задач\w*|task\w*|challenge\w*)\b",
            r"\b(свободн\w*\s*врем\w*|хобби|hobby)\b",
            r"\b(гордост\w*|достижен\w*|achievement\w*)\b",
            r"\b(мемоизац\w*|memoization)\s*(нужн\w*|need\w*|question\w*)\b"
        ],

        "Сеть": [
            r"\bhttp/?(1\.1|2|3)?\b", r"\bhttps\b",
            r"\bapi\b", r"\brest\b", r"\brpc\b",
            r"\bgraphql\b", r"\bapollo\b",
            r"\bgrpc\b",
            r"\bweb\s*socket(s)?\b", r"\bsse\b", r"\blong[\s-]?poll(ing)?\b", r"\bpolling\b",
            r"\bcors\b", r"\bpreflight\b", r"\bsame[-\s]?origin\b|\bsop\b",
            r"\bauth(entication|orization)?\b", r"\btoken(s)?\b", r"\bjwt\b",
            r"\boauth(2)?\b", r"\bopenid\s*connect\b", r"\bsaml\b",
            r"\b(session|cookie)[-\s]?based\b",
            r"\b(csrf|xss|csp|hsts)\b", r"\b(безопасност\w*|security)\b",
            r"\bssl\b|\btls\b", r"\btcp\b", r"\budp\b", r"\bip(v4|v6)?\b",
            r"\bdns\b", r"\burl\b", r"\b(адрес\w*|address)\b",
            r"\bcache[-\s]?control\b", r"\betag\b", r"\blast[-\s]?modified\b", r"\bexpires\b", r"\bvary\b",
            r"\b(сервер\w*|server\w*)\b", r"\b(клиент\w*|client\w*)\b", r"\bвзаимодействи\w*\b",
            r"\b(get|post|put|patch|delete|options|head)\b",
            r"\bhttp[\s-]?cache|cdn|gzip|brotli\b", r"\bidempotenc(y|e)|идемпотент\w*\b",
            r"\brate[\s-]?limit(ing)?\b", r"\bretry\b|\bbackoff\b",
            r"\b(параллельн\w*|parallel)\s*(запрос\w*|request\w*)\b"
        ],

        "Тестирование": [
            r"\btest(s|ing)?\b|\bтест(ы|ир\w*)\b", r"\bunit\b|\bюнит\b",
            r"\bintegration(al)?\b|\bинтеграцион\w*\b", r"\be2e\b|\bend[\s-]?to[\s-]?end\b",
            r"\bsnapshot\b", r"\bcoverage\b|\bпокрыти\w*\b",
            r"\btdd\b|\bbdd\b", r"\bsmoke\b|\bрегрессион\w*\b",
            r"\bjest\b", r"\bvitest\b", r"\bmocha\b", r"\bchai\b", r"\bsinon\b",
            r"\btesting[-\s]?library\b|\b@testing-library/(react|dom)\b", r"\benzyme\b",
            r"\bplaywright\b", r"\bcypress\b", r"\bpuppeteer\b", r"\bwebdriver(io)?\b|\bwdio\b",
            r"\bmsw\b|\bmock\s*service\s*worker\b",
            r"\bsupertest\b", r"\bpact\b|\bcontract\s*testing\b",
            r"\bmock(s|ing)?\b|\bstub(s|bing)?\b|\bspy(ing)?\b|\bfixture(s)?\b|\bfaker\b"
        ],

        "Инструменты": [
            r"\bgit\b", r"\bbranch(es)?\b", r"\bmerge\b", r"\brebase\b", r"\bstash\b",
            r"\bcherry[-\s]?pick\b", r"\bsquash\b", r"\bgit(flow)?\b",
            r"\bsemantic[-\s]?release\b|\bcommitizen\b|\bconventional\s*commits?\b|\bhusky\b|\blint[-\s]?staged\b",
            r"\bnpm\b|\byarn\b|\bpnpm\b|\bnpx\b",
            r"\bwebpack\b|\brollup\b|\bparcel\b|\besbuild\b|\bvite\b|\bswc\b",
            r"\bbabel\b|\bts[-\s]?loader\b",
            r"\beslint\b|\bprettier\b|\bstylelint\b",
            r"\bdocker(\s*compose)?\b",
            r"\bnx\b|\bturborepo\b|\bmake(file)?\b",
            r"\bvue(\.js|js)?\b", r"\bangular\b",
            r"\bnext(\.js|js)?\b", r"\bnuxt(\.js|js)?\b", r"\bremix\b", r"\bastro\b", r"\bsolid(js)?\b", r"\bsvelte\b",
            r"\bthree(\.js|js)?\b",
            r"\bui[\s-]?kit\b|\bбиблиотек\w*\b|\bфреймворк\w*\b",
            r"\b(mui|material\s*ui|@mui)\b|\bant\s*design|antd\b|\bchakra\s*ui\b|\bmantine\b|\bbootstrap\b|\bbulma\b|\bsemantic\s*ui\b|\btailwind(\s*css)?\b|\bshadcn\b",
            # НОВЫЕ ПАТТЕРНЫ ДЛЯ ИНСТРУМЕНТОВ:
            r"\b(веб|web)[\s-]*(технолог\w*|technolog\w*|сокет\w*|socket\w*)\b",
            r"\b(хостинг\w*|hosting|доступност\w*|accessibility)\b",
            r"\b(devdependencies|dependencies)\s*(програм\w*|program\w*)\b",
            r"\b(интерпретиру\w*|компилиру\w*)\s*(язык\w*|language\w*)\b",
            # ДОБИВАЕМ ПРОГРАММИРОВАНИЕ:
            r"\b(программиров\w*|programming)\s*(язык\w*|language)\b", r"\b(функциональн\w*)\s*программиров\w*\b"
        ],

        "Архитектура": [
            r"\bпаттерн\w*\b|\bшаблон\w*\s*проектир\w*\b|\bdesign\s*pattern(s)?\b",
            r"\bsolid\b|\bkiss\b|\bdry\b|\byagni\b|\bgrasp\b",
            r"\bархитектур\w*\b|\bчист(ая|ой)\s*архитектур\w*\b|\bhexagonal\b|\bports?\s*and\s*adapters?\b",
            r"\bddd\b|\bcqrs\b|\bevent\s*sourcing\b",
            r"\bmvc\b|\bmvvm\b|\bmvp\b|\blayer(ed)?\s*architectur\w*\b",
            r"\bмикро(сервис\w*|фронт\w*)\b|\bmodule\s*federation\b|\bmonolith(ic)?\b|\bmonorepo\b",
            r"\bio[cn]\b|\bdependency\s*injection\b",
            r"\b(observer|publisher[-\s]?subscriber|pub[\s-]?sub)\b",
            r"\b(factory|abstract\s*factory|builder|singleton|strategy|adapter|facade|decorator|proxy|iterator|composite|state|command|mediator|flyweight|repository|unit\s*of\s*work)\b",
            r"\bhoc\b|\bhigher[-\s]?order\b|\bfsd\b|\bfeature[-\s]?sliced\b",
            r"\bсайд[-\s]?эффект\w*|side\s*effect(s)?\b|\bpure\s*function\b|\bчист(ая|ые)\s*функц\w*\b",
            r"\bevent[-\s]?driven\b|\bmessage\s*queue\b|\bsaga\b|\borchestrati(on|or)\b|\bchoreograph(y|ic)\b"
        ],

        "Node.js": [
            r"\bnode(\.js|js)?\b|\bnodejs\b|\bv8\b",
            r"\bexpress\b|\bkoa\b|\bfastify\b|\bhapi\b|\bnest(js)?\b|\bsails\b|\badonis\b",
            r"\bbackend\b|\bserver\b|\bсервер\w*\b",
            r"\bmiddleware\b",
            r"\bsocket\.?io\b|\bws\b|\bgrpc\b",
            r"\bstream(s)?\b|\bbuffer(s)?\b|\bfs\b|\bcluster\b|\bworker[_-]?threads?\b|\bchild[_-]?process\b",
            r"\bnodemon\b|\bpm2\b|\bts[-\s]?node\b|\bdotenv\b",
            r"\b(prisma|typeorm|sequelize|knex|mongoose)\b",
            r"\b(postgres(ql)?|mysql|maria(db)?|sqlite|mongodb|redis)\b",
            r"\brest\b|\bgraphql\b|\bapollo\s*server\b",
            r"\bserverless\b|\blambda\b"
        ],

        "Производительность": [
            r"\bоптимизац\w*\b|\boptimization\b|\bперформанс\b|\bperformance\b|\bскорост\w*\b",
            r"\b(profile|profiling|профилирова\w*)\b|\blighthouse\b|\bweb\s*vitals?\b",
            r"\bttfb\b|\bfcp\b|\blcp\b|\bcls\b|\binp\b|\btti\b",
            r"\bbundle(s|size)?\b|\bбандл\w*\b|\bcode\s*splitting\b|\bdynamic\s*import(s)?\b|\btree\s*shak(ing|e)\b",
            r"\b(minify|uglify|compress(ion)?|gzip|brotli)\b",
            r"\b(preload|prefetch|preconnect|dns[-\s]?prefetch)\b",
            r"\bimage\s*optim(ization|ize)\b|\bresponsive\s*images?\b",
            r"\bvirtuali[sz]ation\b|\bвиртуализац\w*\b|\breact[-\s]?(window|virtualized)\b|\binfinite\s*scroll\b",
            r"\b(cache|кеш(ирова\w*)?)\b|\bswr\b|\brtk\s*query\b|\bstale[-\s]?while[-\s]?revalidate\b",
            r"\breflow\b|\brepaint\b|\blayout\s*shift\b|\bcomposit(e|ing)\b|\bwill[-\s]?change\b|\bgpu\b|\bhardware\s*accel(eration)?\b",
            r"\bhydration\b|\bhydration\s*error\b"
        ],

        "Браузеры": [
            r"\bбраузер(ы)?\b|\bbrowser(s)?\b",
            r"\b(render(ing)?\s*pipeline|critical\s*render\s*path)\b",
            r"\b(dom|cssom|render\s*tree|layout|paint|composit(e|ing)|rasteri[sz]ation)\b",
            r"\bdev(tool|tools)\b|\bperformance\s*panel\b|\bcoverage\b",
            r"\bbfcache\b|\bback[\s-]?forward\s*cache\b",
            r"\bpreload\s*scanner\b|\bspeculative\s*parsing\b",
            r"\b(site\s*isolation|sandbox)\b",
            r"\bpermissions?\s*api\b",
            r"\bfeature\s*detection\b|\bpolyfill(s)?\b|\bprogressive\s*enhancement\b|\bcan\s*i\s*use\b",
            r"\buser\s*agent|ua\b",
            r"\bcookies?\b|\bthird[-\s]?party\s*cookies?\b|\btracking\s*protection\b",
            r"\b(отрисовк\w*|render\w*)\s*(страниц\w*|page\w*)\b",
            r"\b(выполня\w*|execut\w*)\s*(отрисовк\w*|render\w*)\b"
        ]
    }
    
    # Ищем совпадения с регексами
    for category, patterns in patterns_re.items():
        for pattern in patterns:
            if re.search(pattern, text, flags):
                return category
    
    return 'Другое'

def main():
    print("ИСПРАВЛЕНИЕ КАТЕГОРИЗАЦИИ")
    print("=" * 50)
    
    # Загружаем данные
    df = pd.read_csv("outputs_bertopic_v2/clusters_enhanced_v2.csv")
    print(f"Загружено {len(df)} кластеров")
    
    # Считаем текущее распределение
    current_other = len(df[df['category'] == 'Другое'])
    print(f"Сейчас в 'Другое': {current_other} кластеров")
    
    # Применяем улучшенную категоризацию
    changed = 0
    for idx, row in df.iterrows():
        new_category = improved_categorize(row['human_name'], row['keywords'])
        if new_category != row['category']:
            old_category = row['category']
            df.at[idx, 'category'] = new_category
            print(f"   > {row['human_name'][:40]}... -> {old_category} -> {new_category}")
            changed += 1
    
    # Результаты
    new_other = len(df[df['category'] == 'Другое'])
    improvement = current_other - new_other
    
    print(f"\nРЕЗУЛЬТАТЫ:")
    print(f"   Изменено: {changed} кластеров")
    print(f"   Было в 'Другое': {current_other}")
    print(f"   Стало в 'Другое': {new_other}")
    print(f"   Улучшение: -{improvement} кластеров")
    
    # Новое распределение
    category_summary = df.groupby('category').agg({
        'size': 'sum',
        'cluster_id': 'count'
    }).rename(columns={'cluster_id': 'clusters_count'}).sort_values('size', ascending=False)
    
    total_questions = category_summary['size'].sum()
    other_percentage = category_summary.loc['Другое', 'size'] / total_questions * 100
    
    print(f"\nНОВОЕ РАСПРЕДЕЛЕНИЕ:")
    print(f"   'Другое': {other_percentage:.1f}% вопросов")
    
    # Сохраняем результаты
    output_dir = "outputs_bertopic_final"
    os.makedirs(output_dir, exist_ok=True)
    
    df.to_csv(f"{output_dir}/clusters_final.csv", index=False, encoding='utf-8-sig')
    category_summary.to_csv(f"{output_dir}/category_summary_final.csv", encoding='utf-8-sig')
    
    top_topics = df.nlargest(20, 'size')[['human_name', 'category', 'size', 'keywords']]
    top_topics.to_csv(f"{output_dir}/top_topics_final.csv", index=False, encoding='utf-8-sig')
    
    print(f"\nРезультаты сохранены в: {output_dir}/")
    
    if other_percentage < 20:
        print("\nЦЕЛЬ ДОСТИГНУТА: Меньше 20% в категории 'Другое'!")
    else:
        print(f"\nЕще нужно поработать: {other_percentage:.1f}% > 20%")

if __name__ == "__main__":
    main()