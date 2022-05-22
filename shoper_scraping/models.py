from django.db import models
from django.utils import timezone

class Departamento(models.Model):
    codigo = models.IntegerField()          # Código ID fornecido pela loja principal
    name = models.CharField(max_length=20)  # Nome do departamento
    url = models.CharField(max_length=20)   # url do departamento

class SubDepartamento(models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)    # departamento relacionado
    codigo = models.IntegerField()          # Código ID fornecido pela loja principal
    name = models.CharField(max_length=50)  # Nome do subdepartamento
    url = models.CharField(max_length=70)   # URL do subdepartamento

class Loja(models.Model):
    name = models.CharField(max_length=50)  # Nome da loja
    ehPrincipal = models.BooleanField()     # True = Loja Principal, False = Loja referência

class Produto(models.Model):
    sku = models.CharField(max_length=10)       # Código interno do produto
    image = models.CharField(max_length=200)    # Imagem do produto
    stock_qty = models.IntegerField()           # Qtde de Estoque do produto
    subdepartamento = models.ForeignKey(SubDepartamento, on_delete=models.CASCADE)  # Subdepartamento em que o produto está inserido
    name = models.CharField(max_length=100)     # Nome do produto
    url = models.CharField(max_length=200)      # Url do produto

class Oferta(models.Model):
    data_captura = models.DateTimeField(default=timezone.now())     # Última atualização
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)        # Loja que está ofertando o produto
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)  # Produto da oferta
    price = models.FloatField()             # Preço da loja de referência
    savingPercentage = models.CharField(max_length=4, null=True)   # Taxa de desconto (apenas para loja principal)
