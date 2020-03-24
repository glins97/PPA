import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "services.settings")
django.setup()
from essay.models import School, Student
juazeiro_ppa_students = [
    'BÁRBARA KARINE SÁ ALVES',
    'BARBARA MARIA ARAUJO DE LUCENA',
    'BEATRIZ CÂNDIDO MONTEIRO DA SILVA',
    'BEATRYZ COÊLHO LOSS',
    'DANIEL PEREIRA BRIGIDO RODRIGUES',
    'DEYSIANE PARENTE DO NASCIMENTO',
    'EDNA PATRÍCIA ANGELO LEITE',
    'EDUARDA FEITOSA BEZERRA',
    'FRANCISCO DE ASSIS GUEDES  DE O. FILHO',
    'GABRIEL CARLOS CARVALHO PINHEIRO',
    'GARDENIA SAMPAIO MOREIRA',
    'GUILHERME MARTINS B. EMERICIANO',
    'HÉRLON HEMERSON SILVA BRITO',
    'HERMES LEANDRO DA SILVA NETO',
    'ISABEL FELIPE VÁSQUEZ',
    'ISADORA DE FARIAS SIQUEIRA',
    'ITALO SANTANA VIEIRA',
    'JORDANIA SILVA MAGALHÃES FERRAZ',
    'JOSÉ ALFREDO SILVA NETO',
    'KAREN BRANDÃO MACIEL CORDEIRO',
    'LARA ALMINO DE SOUZA NOBRE',
    'LARISSA AZEVÊDO FREIRE LEITE',
    'LARÍSSA LACERDA LODONÍO',
    'LARISSA MACHADO ALMEIDA',
    'MARIA GABRIELA FERREIRA CUNHA',
    'MARIA LETICIA MEDEIROS MARINHO',
    'MARIA MADALENA FEITOSA',
    'MARINA GOMES DE CARVALHO',
    'MATHEUS RODRIGUES LINHARES',
    'MONALIZA CORREIA CLAUDINO',
    'MONIC ALVES DE LIMA',
    'NICOLE JOANE PEREIRA E SILVA',
    'OLGA MARIA ARRAIS FIRMINO',
    'PEDRO HENRIQUE XAVIER LOPES',
    'RENATO MORAES DA SILVA',
    'RYLIA PEREIRA RODRIGUES',
    'SALOMAO CRÔCE HERMINIO LEITAO',
    'SARA ARAUJO DE QUENTAL',
    'SUSANA SAMPAIO ARARUNA',
    'TAMMI RAISLA ROCHA GASPAR',
    'TEREZA MARIANA DE OLIVEIRA FREIRE',
    'THIAGO WALLISSON DE OLIVEIRA BARROS',
    'VICTOR LUIZ CALDAS CAMPOS',
]

juazeiro_fera_enem = [
    'ALISSA LAURA AMARO PEREIRA',
    'ANTÔNIO MATHEUS CRUZ PONTES APOLINÁRIO',
    'ARTHUR BRUNO DE ARAUJO VIDAL',
    'ARTHUR RYAN ALMEIDA MENDES',
    'ARTHUR VICTOR DA GRAÇA MACEDO',
    'BEATRIZ LIMA DE ANGELO',
    'CARLOS EMANUEL NOVAIS FERNANDES',
    'DAVI LEITE ALENCAR BEZERRA',
    'FERNANDO LUCAS DE SOUSA TIMOTEO',
    'FRANCISCA HELLEN CHAVES DOS SANTOS',
    'GIOVANNI ALDRIN E SILVA',
    'HEITOR BARROS BANTIM DE VASCONCELOS',
    'HELIO DANIEL ARAUJO LIMA',
    'HEMMILY VITÓRIA DOS SANTOS PARENTE',
    'JOÃO PEDRO DE OLIVEIRA LUSTOSA',
    'KAMILLY CRISTINA DOS SANTOS SILVA',
    'LOURENNY PEDROZA ALVES FIGUEIREDO',
    'MARCELA DA CRUZ ANTUNES',
    'MARCOS VINICIUS ALENCAR DIAS DE OLIVEIRA',
    'MARIA EDUARDA DE MELO CALDAS',
    'MARIA FERNANDA LEITE TAVARES',
    'MARIA LUIZA FEITOSA JUSTO XENOFONTE',
    'MATEUS GONÇALVES DE SOUZA',
    'PEDRO HENRIQUE BARROS DE SÁ',
    'PEDRO LUCAS ALENCAR ALVES',
    'VITÓRIA EMANUELY DA SILA SANTOS',
    'VYCTÓRIA ALCANTARA DE SOUZA',
    'WESLEY CARNEIRO VIEIRA',
    'YGOR JACOB TAVARES BEZERRA',
]

ppa_med_bsb = [
    'BARBARA BATISTA DE PAULA',
    'ANDRE CAVALCANTI STROHER',
    'BERNARDO FERREIRA LOPES ',
    'JÉSSICA DI LUCIA XAVIER  ',
    'JULIA DE OLIVEIRA MACHADO',
    'LUCCA DE AGUIAR MICHELS',
    'GUILHERME LIMA LOPES',
    'ENZO ZANETTI CELENTANO ',
    'HELENA DE SOUSA VALADARES DE CAMARGO',
    'DAVI MONTEIRO DA SILVA',
    'CARLA ALESSANDRA CAVALCANTI',
    'DANIEL ABTIBOL DE MATTOS PEREIRA ',
    'ANA CLARA FARIAS DE NEGRI',
    'DANIELE LEITE FERREIRA',
    'LUIZA MARIA DIAS MEIRELLES ',
    'GABRIELA REZENDE TERTO ',
    'AMANDA RIBERIO MELO ',
    'LETÌCIA CABRAL TORRES',
    'TIAGO DUARTE DO AMARAL MELELO',
    'RAFAEL MORAES DE FARIA ',
    'ANA CECILIA FACCIOLLI BLUM',
    'GABRIELLA RIBEIRO REGO BARROS',
]

ppa_pre_bsb = [
    'EDUARDO RESTIVO',
    'THAINARA MOURA CUNHA',
    'ARON GABRIEL OLINTO ARTIAGA',
    'ESTELA KAREN LIMA SILVA',
    'ANA LUIZA SPINOLA',
    'LUIZA RIGUETTO AUGUSTO',
    'BARBARA STHEFANY QUEIROZ ',
    'PAULA CARVALHO DAMASCENO ',
    'CARLA MASSON DE MATOS ',
    'FELIPE PEREIRA DUTRA ',
    'ANA PAULA RAMOS PIMENTA DA SILVA',
    'LUISA NUNES FERREIRA DE AVILA',
    'BEATRIZ ALVARES FERREIRA MIDLEJ',
    'VINICIOS  RAMSES XAVIER DE BARROS ',
    'GABRIELA ECKERT BULLE ',
    'JOAO PEDRO DE OLIVEIRA SAMPAIO',
    'EDUARDO CORTES VIEIRA ',
    'MARIANA ASSIS HEIDER ',
    'JULLIANA COSTA NEVES ',
    'RENATA REIS DE MOURA ',
    'JEFERSON DE SOUSA RODRIGUES',
    'LUA CLARA FRANCO ROCHA ',
    'MARIA EDUARDA MENDES DE MATOS ',
    'LINDA ARUEIRA E QUARESMA',
    'PEDRO OTÃŒÂVIO OTTONI FERREIRA',
    'VICTOR FELIPE BECKER AMARAL NUNES ',
    'LUIZA DE FREITAS ARAUJO',
    'LUISA BANDEIRA CASTILHO ',
    'MARIA HELENA MIRANDA ',
    'LORENA COSTA DE HOLANDA',
    'ANA CECILIA FACCIOLLI BLUM',
]

ppa_pre_med_bsb = [
    'ANA CLARA WIMMER MACEDO', 
    'DAVI CARVALHO BARBOSA ', 
    'ANA GABRIELA RIBEIRO SAAD', 
    'MARIA DE PAULA GALLO', 
    'MARIA LUIZA DE ORNELAS NOBREGA ', 
    'LEONARDO DIAS GRESPAN DA ROCHA', 
    'JULLIA EDUARDA FEIJO BELLUCO ', 
    'SOFIA SOUSA ALEXANDRE ', 
    'JULIANNE BASILIO DANTAS ', 
    'BIANCA BARBOSA', 
    'BRENO LUCAS SOARES MEDRADO ', 
    'LUANNA CATHARYNA SANTOS DE SOUZA SILVA', 
    'LIZIENNE CALAZANS DE OLIVEIRA ', 
    'GUILHERME RIBEIRO MOTA', 
    'LARA HIORRANA DE SOUZA NASCIMENTO ', 
    'MARYNA MACIEL', 
    'SARAH OBEID STECKELBERG-CONSTANTE', 
    'ANDRÉA ALBUQUERQUE DE SOUZA AVELINO ARRAES', 
    'CARLOS HENRIQUE SILVA DE JESUS ', 
    'VICTORIA HEMILLY DE MORAES SILVERA ', 
    'LORENA COSTA DE HOLANDA', 
    'BRUNA NERES MOREIRA DA FONSECA', 
    'MILENNA DE SOUZA MIRANDA ', 
    'DOUGLAS ARAUJO MENEZES FILHO ', 
    'MARCOS FELIPE PUCCINELLI PORTELA', 
    'HELENA DE SOUSA VALADARES DE CAMARGO', 
    'ANTONIO AUGUSTO MOREIRA BARBOSA', 
    'MARIANA MELLO MENEZES ', 

]
juazeiro = School.objects.get(name='PPA Evolução')
for student_name in juazeiro_ppa_students:
    if len(Student.objects.all().filter(name=student_name)): continue
    Student(
        school=juazeiro,
        name=student_name,
        email='',
        identification='',
        year='',
        class_id='PPA'
    ).save()

for student_name in juazeiro_fera_enem:
    if len(Student.objects.all().filter(name=student_name)): continue
    Student(
        school=juazeiro,
        name=student_name,
        email='',
        identification='',
        year='',
        class_id='Fera ENEM'
    ).save()

ppa = School.objects.get(name='PPA')
for student_name in ppa_med_bsb:
    if len(Student.objects.all().filter(name=student_name.upper())): continue
    Student(
        school=ppa,
        name=student_name.upper(),
        email='',
        identification='',
        year='',
        class_id='MED'
    ).save()
for student_name in ppa_pre_bsb:
    if len(Student.objects.all().filter(name=student_name.upper())): continue
    Student(
        school=ppa,
        name=student_name.upper(),
        email='',
        identification='',
        year='',
        class_id='PRE'
    ).save()
for student_name in ppa_pre_med_bsb:
    if len(Student.objects.all().filter(name=student_name.upper())): continue
    Student(
        school=juazeiro,
        name=student_name.upper(),
        email='',
        identification='',
        year='',
        class_id='PRE MED'
    ).save()