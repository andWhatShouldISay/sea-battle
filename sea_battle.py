from random import randrange
from time import time
from time import sleep
from tkinter import *
from tkinter.messagebox import *
import _thread
import string

class Ship():
	'''
	Класс Ship - реализация поведения объекта корабль для игры "Морской бой"
	свойство (указывается при создании объекта):палубность (1 - 4)
	свойство (указывается при создании объекта):расположение (0 - горизонтальное, 1 - вертикальное)
	свойство (указывается при создании объекта):ключевая точка (тег в формате: "столбец_строка")
	свойство:массив со статусами точек, который формируется конструктором
	свойство:массив с координатами точек корабля, который формируется конструктором
	свойство:координаты точек вокруг корабля
	свойство:статус гибели корабля
	свойство (указывается при создании объекта):префикс тега (для своих кораблей будет, например, "my", для чужих "nmy"
	метод-конструктор:изменение массива со статусами точек, например [0,0,1,0]
	метод:shoot(координаты точки), возвращает 1 - если попали, 2 - убил, 0 - мимо
	'''

	#свойства объектов, описанные в классе
	#длина
	length = 1
	#массив со статусами точек корабля
	status_map = []
	#массив с координатами точек корабля
	coord_map = []
	#точки вокруг корабля
	around_map = []
	#статус гибели корабля
	death = 0
	#префикс тега
	prefix = ""
	#свойство: корабль был создан и не выходит за рамки поля
	ship_correct = 1
	#таг, отвечающий за верхний левый угол
	key_point = ""
	#ориентация
	orient = -1

	#метод-конструктор
	def __init__(self,length,rasp,keypoint):
		self.status_map = []
		self.around_map = []
		self.coord_map = []
		self.death = 0
		self.ship_correct = 1
		self.length = length
		self.key_point = keypoint
		self.orient = rasp		
		#переопределить переменную self.prefix
		self.prefix = keypoint.split("_")[0]
		#создать массивы status_map и coord_map (в зависимости от направления)
		stroka = int(keypoint.split("_")[1])
		stolb = int(keypoint.split("_")[2])
		for i in range(length):
			self.status_map.append(0)
			#в зависимости от направления генерировать новые точки корабля
			#0 - горизонт (увеличивать столбец), 1 - вертикаль (увеличивать строку)
			if stolb + i*(1-self.orient) > 9 or stroka + i*self.orient > 9 or stolb < 0 or stroka < 0:
				self.ship_correct = 0
			if rasp == 0:
				self.coord_map.append(self.prefix+"_"+str(stroka)+"_"+str(stolb+i))
			else:
				self.coord_map.append(self.prefix+"_"+str(stroka+i)+"_"+str(stolb))
		for point in self.coord_map:
			ti = int(point.split("_")[1])
			tj = int(point.split("_")[2])
			for ri in range(ti-1,ti+2):
				for rj in range(tj-1,tj+2):
					if ri>=0 and ri<=9 and rj>=0 and rj<=9:
						if not(self.prefix+"_"+str(ri)+"_"+str(rj) in self.around_map) and not(self.prefix+"_"+str(ri)+"_"+str(rj) in self.coord_map):
							self.around_map.append(self.prefix+"_"+str(ri)+"_"+str(rj))

	#выстрел
	def shoot(self,shootpoint):
		#определить номер точки и изменить её статус
		status = 0
		for point in range(len(self.coord_map)):
			if self.coord_map[point] == shootpoint:
				self.status_map[point] = 1
				status = 1
				break
		if not(0 in self.status_map):
			status = 2
			self.death = 1
		return status

	#подвинуть корабль
	def move(self,dx,dy):
		arr=self.key_point.split("_")
		new_ship=Ship(self.length,self.orient,arr[0]+"_"+str(int(arr[1])+dx)+"_"+str(int(arr[2])+dy))
		if new_ship.ship_correct:
			self=new_ship
		return self
				
	
	#повернуть корабль
	def rotate(self):
		new_ship=Ship(self.length,1-self.orient,self.key_point)				
		if new_ship.ship_correct:
			self=new_ship
		return self
		


class Application(Frame):
	'''
	Приложение. Наследует класс Frame. Создание окна, холста и всех функций для реализации приложения
	'''
	#ширина рабочего поля
	width = 800
	#высота рабочего поля
	height = 400
	#цвет фона холста
	bg = "lightcyan"
	#отступ между ячейками
	indent = 2
	#размер одной из сторон квадратной ячейки
	gauge = 32
	#смещение по y (отступ сверху)
	offset_y = 40
	#смещение по x пользовательского поля
	offset_x_user = 30
	#смещение по x поля компьютера
	offset_x_comp = 430
	#компьютерный флот
	fleet_comp = []
	#наш флот
	fleet_user = []
	#использованные клетки
	fleet_user_array = []
	lengths=[]
	#массив точек, в которые стрелял компьютер
	comp_shoot = []
	#массив точек, в которые попал компьютер, но ещё не убил
	comp_hit = []	

	cur_ship=None	

	#добавление холста на окно
	def createCanvas(self):
		self.canv = Canvas(self)
		self.canv["height"] = self.height
		self.canv["width"] = self.width
		self.canv["bg"] = self.bg
		self.canv.pack()
		self.canv.focus_set()
		#установка кораблей юзера
		self.canv.bind("<Return>",self.creatingUserFleetEnter)
		self.canv.bind("<Key>",self.creatingUserFleetSpace)
		self.canv.bind("<Down>",self.creatingUserFleetDown)
		self.canv.bind("<Right>",self.creatingUserFleetRight)
		self.canv.bind("<Left>",self.creatingUserFleetLeft)
		self.canv.bind("<Up>",self.creatingUserFleetUp)
		#клик по холсту вызывает функцию play
		self.canv.bind("<Button-1>",self.userPlay)

	def new_game(self):
		self.fleet_user = []
		self.fleet_user_array = []
		self.lengths = [1,1,1,1,2,2,2,3,3]
		self.canv.delete('all')
		#добавление игровых полей пользователя и компьютера
		#создание поля для пользователя
		#перебор строк
		for i in range(10):
			#перебор столбцов
			for j in range(10):
				xn = j*self.gauge + (j+1)*self.indent + self.offset_x_user
				xk = xn + self.gauge
				yn = i*self.gauge + (i+1)*self.indent + self.offset_y
				yk = yn + self.gauge
				#добавление прямоугольника на холст с тегом в формате:
				#префикс_строка_столбец
				self.canv.create_rectangle(xn,yn,xk,yk,tag = "my_"+str(i)+"_"+str(j))

		#создание поля для компьютера
		#перебор строк
		for i in range(10):
			#перебор столбцов
			for j in range(10):
				xn = j*self.gauge + (j+1)*self.indent + self.offset_x_comp
				xk = xn + self.gauge
				yn = i*self.gauge + (i+1)*self.indent + self.offset_y
				yk = yn + self.gauge
				#добавление прямоугольника на холст с тегом в формате:
				#префикс_строка_столбец
				self.canv.create_rectangle(xn,yn,xk,yk,tag = "nmy_"+str(i)+"_"+str(j),fill="gray")

		#добавление букв и цифр
		for i in reversed(range(10)):
			#цифры пользователя
			xc = self.offset_x_user - 15
			yc = i*self.gauge + (i+1)*self.indent + self.offset_y + round(self.gauge/2)
			self.canv.create_text(xc,yc,text=str(i+1))
			#цифры компьютера
			xc = self.offset_x_comp - 15
			yc = i*self.gauge + (i+1)*self.indent + self.offset_y + round(self.gauge/2)
			self.canv.create_text(xc,yc,text=str(i+1))
		#буквы
		symbols = "АБВГДЕЖЗИК"
		for i in range(10):
			#буквы пользователя
			xc = i*self.gauge + (i+1)*self.indent + self.offset_x_user + round(self.gauge/2)
			yc = self.offset_y - 15
			self.canv.create_text(xc,yc,text=symbols[i])

			#буквы компьютера
			xc = i*self.gauge + (i+1)*self.indent + self.offset_x_comp + round(self.gauge/2)
			yc = self.offset_y - 15
			self.canv.create_text(xc,yc,text=symbols[i])

		#генерация кораблей противника
		self.createnmyships("nmy")
		self.cur_ship=Ship(4,0,"my_0_0")
		self.paintUnreadyShip(self.cur_ship)

	def createnmyships(self, prefix="nmy"):
		#функция генерации кораблей на поле
		#количество сгенерированных кораблей
		count_ships = 0
		while count_ships < 10:
			#массив занятых кораблями точек
			fleet_array = []
			#обнулить количество кораблей
			count_ships = 0
			#массив с флотом
			fleet_ships = []
			#генерация кораблей (length - палубность корабля)
			for length in reversed(range(1,5)):
					#генерация необходимого количества кораблей необходимой длины
					for i in range(5-length):
						#генерация точки со случайными координатами, пока туда не установится корабль
						try_create_ship = 0
						while 1:
							try_create_ship += 1
							#если количество попыток превысило 50, начать всё заново
							if try_create_ship > 50:
								break
							#генерация точки со случайными координатами
							ship_point = prefix+"_"+str(randrange(10))+"_"+str(randrange(10))
							#случайное расположение корабля (либо горизонтальное, либо вертикальное)
							orientation = randrange(2)
							#создать экземпляр класса Ship
							new_ship = Ship(length,orientation,ship_point)
							#если корабль может быть поставлен корректно и его точки не пересекаются с уже занятыми точками поля
							#пересечение множества занятых точек поля и точек корабля:
							intersect_array = list(set(fleet_array) & set(new_ship.around_map+new_ship.coord_map))
							if new_ship.ship_correct == 1 and len(intersect_array) == 0:
								#добавить в массив со всеми занятыми точками точки вокруг корабля и точки самого корабля
								fleet_array += new_ship.coord_map
								fleet_ships.append(new_ship)
								count_ships += 1
								break
		self.fleet_comp = fleet_ships

	#юзер жмёт Enter
	def creatingUserFleetEnter(self,e):
		if len(self.fleet_user)<10:
			#если корабль монжо поместить на это место, то помещаем туда и переходим к следующему
			intersect_array = list(set(self.fleet_user_array) & set(self.cur_ship.around_map+self.cur_ship.coord_map))
			if self.cur_ship.ship_correct == 1 and len(intersect_array) == 0:
				self.fleet_user_array += self.cur_ship.coord_map
				self.fleet_user.append(self.cur_ship)
				self.paintReadyShip(self.cur_ship)
				if len(self.lengths):
					self.cur_ship=Ship(self.lengths.pop(),0,"my_0_0")
					self.paintUnreadyShip(self.cur_ship)					

	def creatingUserFleetDown(self,e):
		if len(self.fleet_user)<10:
			self.fillRedInLightCyan(self.cur_ship)
			self.cur_ship=self.cur_ship.move(1,0)
			self.paintUnreadyShip(self.cur_ship)

	def creatingUserFleetUp(self,e):
		if len(self.fleet_user)<10:
			self.fillRedInLightCyan(self.cur_ship)
			self.cur_ship=self.cur_ship.move(-1,0)
			self.paintUnreadyShip(self.cur_ship)
	
	def creatingUserFleetLeft(self,e):
		if len(self.fleet_user)<10:
			self.fillRedInLightCyan(self.cur_ship)
			self.cur_ship=self.cur_ship.move(0,-1)
			self.paintUnreadyShip(self.cur_ship)

	def creatingUserFleetRight(self,e):
		if len(self.fleet_user)<10:
			self.fillRedInLightCyan(self.cur_ship)
			self.cur_ship=self.cur_ship.move(0,1)
			self.paintUnreadyShip(self.cur_ship)

	def creatingUserFleetSpace(self,e):
		if len(self.fleet_user)<10 and e.char==' ':
			self.fillRedInLightCyan(self.cur_ship)
			self.cur_ship=self.cur_ship.rotate()
			self.paintUnreadyShip(self.cur_ship)

	
	

	def fillRedInLightCyan(self,S):
		for point in S.coord_map:
			self.canv.itemconfig(point,fill="lightcyan")
		for ship in self.fleet_user:
			for point in ship.coord_map:
				self.canv.itemconfig(point,fill="gray")	

	def paintUnreadyShip(self,S):
		for point in S.coord_map:
			self.canv.itemconfig(point,fill="red")

	#метод для отрисовки корабля
	def paintReadyShip(self,S):
		#отрисовка корабля
		for point in S.coord_map:
			self.canv.itemconfig(point,fill="gray")
	#метод рисования в ячейке креста на белом фоне
	def paintCross(self,xn,yn,tag):
		xk = xn + self.gauge
		yk = yn + self.gauge
		self.canv.itemconfig(tag,fill="white")
		self.canv.create_line(xn+2,yn+2,xk-2,yk-2,width="3")
		self.canv.create_line(xk-2,yn+2,xn+2,yk-2,width="3")

	#метод рисования промаха
	def paintMiss(self,point):
		#найти координаты
		new_str = int(point.split("_")[1])
		new_stlb = int(point.split("_")[2])
		if point.split("_")[0] == "nmy":
			xn = new_stlb*self.gauge + (new_stlb+1)*self.indent + self.offset_x_comp
		else:
			xn = new_stlb*self.gauge + (new_stlb+1)*self.indent + self.offset_x_user
		yn = new_str*self.gauge + (new_str+1)*self.indent + self.offset_y
		#добавить прямоугольник
		#покрасить в белый
		self.canv.itemconfig(point,fill="white")
		self.canv.create_oval(xn+13,yn+13,xn+17,yn+17,fill="gray")

	#метод проверки финиша
	def checkFinish(self,type):
		'''type - указание, от чьего имени идёт обращение'''
		status = 0
		if type == "user":
			for ship in self.fleet_comp:
				status += ship.death
		else:
			for ship in self.fleet_user:
				status += ship.death
		return status

	#метод игры компьютера

	def compPlay(self):
		sleep(1)
		#если нет точек, в которые попал, но не убил то генерировать случайные точки
		if len(self.comp_hit)==0:
			#генерировать случайные точки, пока не будет найдена пара, которой не было в списке выстрелов
			while 1:
				i = randrange(10)
				j = randrange(10)
				if not("my_"+str(i)+"_"+str(j) in self.comp_shoot):
					break
		#если есть одна такая точка
		elif len(self.comp_hit)==1:
			#массив точек вокруг
			points_around = []
			i = int(self.comp_hit[0].split("_")[1])
			j = int(self.comp_hit[0].split("_")[2])
			for ti in range(i-1,i+2):
				for tj in range(j-1,j+2):
					if ti>=0 and ti<=9 and tj>=0 and tj<=9  and (ti == i or tj == j) and not(ti == i and tj == j) and not("my_"+str(ti)+"_"+str(tj) in self.comp_shoot):
						points_around.append([ti,tj])
			#cлучайная точка из массива
			select = randrange(len(points_around))
			i = points_around[select][0]
			j = points_around[select][1]	
		else:
			#если есть больше одной такой точки
			points_to_strike = []
			self.comp_hit.sort()
			#если у таких точек сопадает первая координата
			if self.comp_hit[0][3]==self.comp_hit[1][3]:
				#проверяем точку слева от найденных
				if self.comp_hit[0][5]!='0':
					arr=self.comp_hit[0].split('_')
					arr[2]=str(int(arr[2])-1)
					arr=arr[0]+'_'+arr[1]+'_'+arr[2]
					if not arr in self.comp_shoot:
						points_to_strike.append(arr)
				#справа
				if self.comp_hit[-1][5]!='9':
					arr=self.comp_hit[-1].split('_')
					arr[2]=str(int(arr[2])+1)
					arr=arr[0]+'_'+arr[1]+'_'+arr[2]
					if not arr in self.comp_shoot:
						points_to_strike.append(arr)				
			else:
				#сверху
				if self.comp_hit[0][3]!='0':
					arr=self.comp_hit[0].split('_')
					arr[1]=str(int(arr[1])-1)
					arr=arr[0]+'_'+arr[1]+'_'+arr[2]
					if not arr in self.comp_shoot:
						points_to_strike.append(arr)
				#снизу				
				if self.comp_hit[-1][3]!='9':
					arr=self.comp_hit[-1].split('_')
					arr[1]=str(int(arr[1])+1)
					arr=arr[0]+'_'+arr[1]+'_'+arr[2]
					if not arr in self.comp_shoot:
						points_to_strike.append(arr)
			#случайная точка (не больше двух)
			selected=points_to_strike[randrange(len(points_to_strike))]
			i=int(selected.split('_')[1])
			j=int(selected.split('_')[2])
		xn = j*self.gauge + (j+1)*self.indent + self.offset_x_user
		yn = i*self.gauge + (i+1)*self.indent + self.offset_y
		hit_status=0
		for obj in self.fleet_user:
			#если координаты точки совпадают с координатой корабля, то вызвать метод выстрела
			if "my_"+str(i)+"_"+str(j) in obj.coord_map:
				hit_status=2
				#изменить статус попадания
				self.comp_hit.append("my_"+str(i)+"_"+str(j))
				#мы попали, поэтому надо нарисовать крест
				self.paintCross(xn,yn,"my_"+str(i)+"_"+str(j))
				#добавить точку в список выстрелов компьютера
				self.comp_shoot.append("my_"+str(i)+"_"+str(j))
				#если метод вернул двойку, значит, корабль убит
				if obj.shoot("my_"+str(i)+"_"+str(j)) == 2:
					#изменить статус корабля
					obj.death = 1
					#все точки вокруг корабля сделать точками, в которые мы уже стреляли
					for point in obj.around_map:
						#нарисовать промахи
						self.paintMiss(point)
						#добавить точки вокруг корабля в список выстрелов компьютера
						self.comp_shoot.append(point)
					showinfo("","Убил!")
					self.comp_hit.clear()
				else:
					showinfo("","Попал!")
				break
		#если статус попадания остался равным нулю - значит, мы промахнулись, передать управление компьютеру
		#иначе дать пользователю стрелять
		if hit_status == 0:
			#добавить точку в список выстрелов
			self.comp_shoot.append("my_"+str(i)+"_"+str(j))
			self.paintMiss("my_"+str(i)+"_"+str(j))
			showinfo("","Мимо!")
		else:
			#проверить выигрыш, если его нет - передать управление компьютеру
			if self.checkFinish("comp") < 10:
				self.compPlay()
			else:
				showinfo("", "Победил компьютер!")

	#метод для игры пользователя
	def userPlay(self,e):
		if len(self.fleet_user)==10:
			for i in range(10):
				for j in range(10):
					xn = j*self.gauge + (j+1)*self.indent + self.offset_x_comp
					yn = i*self.gauge + (i+1)*self.indent + self.offset_y
					xk = xn + self.gauge
					yk = yn + self.gauge
					if e.x >= xn and e.x <= xk and e.y >= yn and e.y <= yk:
						#проверить попали ли мы в корабль
						hit_status = 0
						for obj in self.fleet_comp:
							#если координаты точки совпадают с координатой корабля, то вызвать метод выстрела
							if "nmy_"+str(i)+"_"+str(j) in obj.coord_map:
								#изменить статус попадания
								hit_status = 1
								#мы попали, поэтому надо нарисовать крест
								self.paintCross(xn,yn,"nmy_"+str(i)+"_"+str(j))
								#если метод вернул двойку, значит, корабль убит
								if obj.shoot("nmy_"+str(i)+"_"+str(j)) == 2:
									#изменить статус корабля
									obj.death = 1
									#все точки вокруг корабля сделать точками, в которые мы уже стреляли
									for point in obj.around_map:
										#нарисовать промахи
										self.paintMiss(point)
									showinfo("","Вы потопили корабль!")
								else:
									showinfo("","Вы попали!")
								break
						#если статус попадания остался равным нулю - значит, мы промахнулись, передать управление компьютеру
						#иначе дать пользователю стрелять
						if hit_status == 0:
							self.paintMiss("nmy_"+str(i)+"_"+str(j))
							showinfo("","Вы промахнулись!")
							#проверить выигрыш, если его нет - передать управление компьютеру
							if self.checkFinish("user") < 10:
								self.compPlay()
							else:
								showinfo("Морской бой", "Победил игрок!")
						elif self.checkFinish("user")==10:
							showinfo("Морской бой", "Победил игрок!")
						break

	#метод закрытия окна
	def quit_game(self):
		root.destroy()

	def __init__(self, master=None):
		#инициализация окна
		Frame.__init__(self, master)
		self.pack()

		#инициализация меню
		self.m = Menu(master)
		master.config(menu = self.m)
		self.m_play = Menu(self.m)
		self.createCanvas()
		self.m.add_command(label = "Новая игра", command = self.new_game)
		self.m.add_command(label = "Выход", command = self.quit_game)
		#вызов функции создания холста
		#событие закрытия окна
		root.protocol("WM_DELETE_WINDOW", self.quit_game)
		root.mainloop()

#инициализация окна
root = Tk()
root.title('Морской бой')
root.geometry("800x400+100+100")

#инициализация приложения
app = Application(root)
app.mainloop()
