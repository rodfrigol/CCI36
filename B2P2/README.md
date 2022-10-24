# CCI36

### Obtenção das propriedades dos triângulos

A função get_doc faz o parse do XML. A partir disso foram obtidos as cordenadas e cores dos três vértices do triângulo na função get_triangles para calcular a área, a normal, o centróide e a cor por meio das funções get_color, get_normal_and_area e get_centroid. 
Para o cáculo dos pontos foi levado em consideração a variação de escala e localização dos pontos.
```
x = float(points_arr[offset]) * scaleX + locX
y = float(points_arr[offset + 1]) * scaleY + locY
z = float(points_arr[offset + 2]) * scaleZ + locZ
```

A cor é calculada como a média da cor dos três vértices. A normal e a área foram calculadas usando os métodos numpy.cross (produto vetorial) e numpy.linalg.norm (módulo do vetor). O centróide é cálculado a partir da média das coordenadas dos 3 vértices.

```
cross = np.cross(p2 - p1, p3 - p1)
norm = np.linalg.norm(cross)
self.normal = cross / norm
self.area = norm / 2
```

### Cálculo dos Fatores de Forma

A função get_form_factors cria uma mátriz 2x2 com os fatores de forma que serão calculados pela função get_ff.

Existem três situações em que a função get_ff retorna zero. 
Se a distância entre os triângulos for zero, pois seria o mesmo triângulo.
Se o cosseno do ângulo formado pela normal de um dos triângulos e a reta que liga os dois centróides for menor que zero, o que indica que o ângulo é maior que 90 graus e então os triângulos estão virados para lados opostos.
Se houver algum centróide com uma distância menor que 0.2 (valor obtido de forma experimental) em relação à reta que liga os dois centróides, o que é verificado na função has_intersection.

Caso nenhuma dessas três situações ocorra, calculamos o fator de forma por meio da fórmula:
```
(cos01 * cos02 * t2.area) / (np.pi * r2 + t2.area)
```

### Cálculo das respostas

Nessa etapa a função solve_equations completa as matrizes do sistema de equação de radiosidade para cada uma das cores.
Para isso, preenchemos a matriz n x n com o valor -p[i] * form_factors[i][j]. Por fim, usamos o método numpy.linalg.inv para inverter a matriz nx n e numpy.matmul para multiplicar a matriz n x n pela matriz coluna com os parâmetros E.
Após isso usamos o fator de normalização 200 para ajustar a intensidade das cores.

### Novo arquivo

Por fim, subistituímos os vetores de cor no novo arquivo output.dae com os resultados obtidos.

### Conclusão

Através da cena obtida através do arquivo output.dae podemos perceber que conseguimos obter os efeitos esperados.
Quando há um objeto no meio do caminho ocorre sombra e o objeto alvo não é iluminado.
Caso uma parte não esteja virada de frente para outra a luz não incide sobre ela.
Quanto mais próximo um objeto do outro e quanto menor o ângulo entre as normais e a reta que liga dois objetos a iluminação fica mais intensa.
Um objeto que recebe iluminação é capaz de refletir essa iluminação.
