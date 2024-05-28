УДК 621.91:67.05 

# Разработка автоматического алгоритма калибровки камеры для определения координат заготовки на рабочем столе станка с ЧПУ

*Рассматривается возможный подход к решению задачи об автоматической калибровке камеры, входящая в состав оптической схемы разработанного станка, при решении задачи индентификации местоположения контура заготовки печатной платы на рабочей области CNC станка. **Практическая значимость**: разработанный алгоритм позволит сократить время калибровки камеры при пуско-наладочных работах на разработанном ЧПУ станке (тут бы поправить боллее адекватно).* 

***Ключевые слова:*** исправление дисторсии, CNC станок, идентификация рабочей области, OpenCV, Canny, Python, Raspberry Pi.


**Введение.** При малосерийном или штучном изготовлении электронного оборудования одним из этапов является изготовление печатной платы - изделия, состоящее из плоского изоляционного основания с отверстиями, пазами, вырезами и системой проводников, которое используют для установки компонентов в соответствии с электрической принципиальной схемой. Достоаточно часто на этом этапе заготовку печатной платы изготавливают методом фрезеровки и сверления на CNC станке. Для наилучшего качества полученной платы требуется точное определение координат расположения заготовки. Высокая точность определения позволяет производить обработку детали с двух сторон, что необходимо для большинства изделий.

**Обзор аналогов.** Исследователи из Орхусского университета [1] разрабатывают систему ЧПУ для лазерного резака на основе комбинирования маркеров и дополненной реальности. Система основана на подходе WYSIWYG (What You See Is What You Get (англ.) — что видите, то и получаете), где проектор используется для отображения текущих контуров, а маркеры используются для установки его положения в рабочей области. Наряду с этим специалисты университета Кейо [2] расширяют функциональность фидуциальных маркеров для лазерного резака. Чтобы установить параметры резки, они размещают набор маркеров опорных точек рядом с заготовкой, в том числе метки, связанные с материалом, порядком операций и командами. В работе [3] описан способ обнаружения ошибок контура на основе машинного зрения. Разработан специальный измерительный прибор с нанесенными на него маркерами, который позволяет измерять погрешность контура без сетчатого датчика. В работе [4] предлагается метод прямой симуляции обрабатывающего инструмента станка. Здесь маркеры используются для определения положения инструмента и заготовки; дополненная реальность — для моделирования траектории инструмента при обработке. 

**Обзор трёхкоординатной устновки CNC-станка для производства печатных плат.** Помимо стандартных компонентов трёхкоординтной системы (шаговые двигатели, рабочий стол, инструмент), на установке (рис. 1) присутствуют две камеры, общего вида и уточняющая, которые являются компонентами системы технического зрения для определения координат заготовки. Камера общего вида жёстко закрепленна на станке и обозревает рабочую область целиком, что обеспечивает повторяемость обработки. Уточняющяя камера жестко закреплена на хоботе станка, что позволяет проводить измерения в произвольном месте рабочего стола и обеспечивает неизменность расстояния от оптической оси камеры до оси вращения инструмента.

![Рисунок 1. Трёхкоординатная устновка CNC-станка для производства печатных плат](img/stanok1.jpg "Рисунок 1 - Трёхкоординатная устновка CNC-станка для производства печатных плат")

Рисунок 1 - Трёхкоординатная устновка CNC-станка для производства печатных плат

Все вычисления и управление шаговыми двигателями выполняются на микрокомпьютере Raspberry Pi [7]. Система разрабатывалась на языке программирования Python 3.9 [8] при использовании библиотки OpenCV 4.1.8 [9], для работы с техническим зрением, библиотека RPi.GPIO [11], для работы с универсальными портами ввода вывыдa микрокомпьютера, которые управляют механикой станка. Вышеописанные инструменты и средства разработаны продиктованы условиями технического задания.

**Алгоритм работы системы.** С учетом поставленной задачи и имеющихся средств был разработан алгоритм работы системы идентификации заготовки печатной платы (Рисунок 2).

![Рисунок 2. Алгоритм работы системы идентификации заготовки печатной платы](img/algortim.svg "Рисунок 2 - Алгоритм работы системы идентификации заготовки печатной платы"]

Рисунок 2 - Алгоритм работы системы идентификации заготовки печатной платы

На первом этапе происходит исправление перспективы изображения общего вида рабочей области. 
Для исправления перспективы съемка велась таким образом, чтобы рабочий стол помещался в поле зрения камеры с достаточными "полями", затем в графическом редакторе были получены фактические  координаты четырёх углов стола и требуемые координаты для исправления перспективы, из полученных данных строилась матрица преобразования при помощи функции cv2.getPerspectiveTransform (src, dst) [9]. При её применении к изображению, а также пропустив изображение через функцию cv2.warpPerspective (src, M, dsize) [9] мы получаем  изображение в нужной проекции. Остаётся только обрезать изображение по контуру рабочего стола и передать его следующим функциям системы. 

На втором этапе выполняется идентификация положения заготовки на изображении общего вида рабочей области. В работе [5] рассмотрено решение подобной задачи, но в условиях нашей задачи мы можем упростить работу, так как мы знаем размер заготовки (заготовки печатных плат имеют известные параметры ширины, выстоты и толщины) [10]. Применив функцию cv2.findContours() [9], мы получим список всех найденных на изображении контуров. Посчитав диагональ, меньшую и большую стороны каждого контура и зная диагональ, меньшую и большую стороны искомого, выбираем нужный контур и передаём координаты углов контура следующим функциям системы (рис. 3).

![Рисунок 3. Результат идентификации контура заготовки печатной платы по изображению с камеры общего вида](img/find_plate_perspective_out_0_525_979_737.jpg "Рисунок 3. Результат идентификации контура заготовки печатной платы по изображению с камеры общего вида")

Рисунок 3 - Результат идентификации контура заготовки печатной платы по изображению с камеры общего вида

На последнем этапе необходимо выполнить уточнение координат угла заготовки печатной платы по дополнительной камере. Получив на предыдущем шаге координату угла контура, нообходимо переместить центр камеры по этой координате и получить снимок. Последующие алгоритмы потребуют работу с изображением в двухканальном представлении, для этого применим к исходному изображению функцию cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) [9], где img - это исходное изображение, а cv2.COLOR_BGR2GRAY - требуемый цветовой фильтр. В работе [5] приведено преимущество использования метода сегментации Канни [6], который мы и применим к нашему изображению, получив изображение с краями. Эту информацию необходимо отдать на обработку функции cv2.HoughLinesP [9], которая отдаст нам все линии на изображении. Далее разделим линии на две группы: те которые "более горизонтальные" и те которые "более вертикальные". Мы можем так поступить т.к. заготовка изначально имеет прямоугольную форму. Из каждой группы необходимо методом кластеризации выбрать линюю, вокруг которой будет больше всего точек, образующих контуры, эта линии и будут образовывать вертикальный и горизонтальный край заготовки. Наконец надо определить точку пересечения этих линий - это угол платы, а так же посчитать смещение относительно центра снимка.

Далее, переместив камеру на найденное смещение, повторяем вышеописанную процедуру, пока смещение не составит меньше чем одна десятая доля миллиметра. Так же повторяем всё это с остальными углами получая уточненное значение углов заготовки (рис. 4). Полученные координаты передаются следующим системам управления CNC-станка.

![Рисунок 4. Результат идентификации угла заготовки печатной платы по изображению с уточняющей камеры](img/out_2_4343_rotate.jpg "Результат идентификации угла заготовки печатной платы по изображению с уточняющей камеры")

Рисунок 4 - Результат идентификации угла заготовки печатной платы по изображению с уточняющей камеры. 

**Заключение.** В данной работе было рассмотренно решение задачи идентификации положения заготовки печатной платы на рабочей области CNC станка. Точность определения координат составила менее одной десятой миллиметра, что достаточно для создания большинства малосерийных изделий. Алгоритм работает полностью в автоматическом режиме, а полученной точности достаточно для обработки детали с двух сторон.

## Список использованных источников ##

1. Winge K., Haugaard R., and Merritt T. Val: Visually augmented laser cutting to enhance and support creativity //
IEEE Intern. Symp. on Mixed and Augmented Reality — Media, Art, Social Science, Humanities and Design
(ISMAR-MASH’D). 2014. September. P. 31—34.

2. Kikuchi T., Hiroi Y., Smith R., Thomas B., and Sugimoto M. Marcut: Marker-based laser cutting for personal
fabrication on existing objects // TEI 2016 — Proc. of the 10th Anniversary Conf. on Tangible Embedded and
Embodied Interaction. Association for Computing Machinery. 2016. P. 468—474.

3. Li X., Liu W., Pan Y., Li H., Ma X., and Jia Z. A monocular-vision based contouring error detection method for CNC
machine tools // IEEE Intern. Instrumentation and Measurement Technology Conf. (I2MTC). 2018. May. P. 1—6.

4. Kiswanto G. and Ariansyah D. Development of augmented reality (ar) for machining simulation of 3-axis cnc
milling // Intern. Conf. on Advanced Computer Science and Information Systems (ICACSIS). 2013. September.
P. 143—148.

5. Алгоритм нахождения контура делового остатка нестандартной формы по цифровой фотографии средствами языка программирования Python на основе библиотеки компьютерного зрения Opencv / В. Р. Зайникова, С. А. Зыкин, Р. А. Файзрахманов // Вестник Пермского национального исследовательского политехнического университета. Электротехника, информационные технологии, системы управления = Perm National Research Polytechnic University Bulletin. Electrotechnics, Information Technologies, Controlsystems. - 2020. - № 35. - С. 133-151.

6. Canny J.E. A computational approach to edge detection // IEEE Trans Pattern Analysis and Machine Intelligence. – 1986. – No. 8. – Р. 679–698.

7. Raspberry Pi Documentation // www.raspberrypi.com URL: https://www.raspberrypi.com/documentation/ (дата обращения: 16.5.2023)

8. Our Documentation | Python.org // www.python.org URL: https://www.python.org/doc/ (дата обращения: 16.5.2023)

9. OpenCV: OpenCV-Python Tutorials // docs.opencv.org URL: https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html (дата обращения: 16.5.2023)

10. Макетные платы и стеклотекстолит | купить в розницу и оптом // www.chipdip.ru URL: https://www.chipdip.ru/catalog/breadboards (дата обращения: 16.5.2023)

11. RPi.GPIO  // sourceforge.net URL: https://sourceforge.net/projects/raspberry-gpio-python/ (дата обращения: 16.5.2023)
