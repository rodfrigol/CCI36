# CCI36

### Para a renderização

Criou-se uma variável renderer, que recebe um objeto WebGLRenderer(), do Three.js, capaz de realizar operações necessárias de renderização. Adicionou-se esse objeto ao document body do html.

### Renderização de objetos dinâmicos

Montou-se uma função auxiliar createElements() que usa uma lista de objetos com as características adequadas aos constructors das funções do three.js para as formas geométricas que desejava-se renderizar. A partir das características, verifica-se o tipo do elemento a ser criado e é invocada a função que retorna objeto geométrico desejado. Usou-se a função mesh do Three.js para conjugar a geometria com caracterísicas como a cor e criar um elemento el. Por fim, setou-se a posição do elemento e adicionou este ao cenário.
```
 function createElements() {
                let geometry, material, el;
                for(let i = 0; i < elements.length; i++) {
                    if (elements[i].type === "rectangle") {
                        geometry = new THREE.BoxGeometry(elements[i].width, elements[i].height, 1);
                    }
                    ...
                    el = new THREE.Mesh(geometry, material);
                    ...
                    el.static = false
                    scene.add(el);
                }
}
```

### Renderização de objetos estáticos

Montou-se uma função auxiliar createStaticElement() que seguiu a mesma lógica da função create Elements, com o detalhe de, na realidade, setar el.static como verdadeira. 

Aqui o detalhe foi se aproveitar de um filtro que verifica o atributo static do elemento adicionado ao objeto Scene:

```
            createElements();
            createStaticElement();
            const children = scene.children.filter(el => !el.static);
```

Assim, ao invocar-se alguma alteração nos objetos, eram chamados apenas aqueles com static = false - tornando os demais de fato estáticos.

### Hover

### Drag suave e com limites

### Rotate com mousewheel

### Rotate suave com mouse2

### Função de cálculo de área
Para lidar com o cálculo da área de um polígono em outro, utilizou-se as funcionalidades presentes na classe Raycaster, do Three.js. Aproveitou-se o fato desse objeto ser capaz de verificar se, dentro de um certo raio, havia outro objeto a nossa escolha intersectando. 

´´´
  function intersectionArea() {
                let ray = new THREE.Raycaster();
                ...
´´´

Dentro da classe do Raycaster:

```
       intersectObjects(objects, recursive = true, intersects = []) {
			for (let i = 0, l = objects.length; i < l; i++) {
				intersectObject(objects[i], this, intersects, recursive);
			}

			intersects.sort(ascSort);
			return intersects;
		}
```

Então varreu-se a área com for loops, verificando com passo de 0.01 a cada iteração se havia intersecção entre o objeto estático e o dinâmico e foi-se acumulando a intersecção em variáveis auxiliares que por fim compuseram uma razão de áreas.

```
                        aux = ray.intersectObjects(scene.children);
                        has_static = false;
                        has_non_static = false;
                        for (z = 0; z < aux.length; z++) {
                            if (aux[z].object.static)
                                has_static = true;
                            else
                                has_non_static = true;
                        }
                        if (has_static) {
                            static_area ++;
                            if (has_non_static)
                                non_static_area ++;
                        }

```


### Aviso de fim do jogo
Para criar o aviso de fim de jogo foi feito um event listener que, toda vez que o botão esquerdo do mouse é solto, verifica se a área de intersecção é maior que 0.95, através da função intersectionArea(). Caso seja ele muda o CSS do elemento que continha a mensagem que inicialmente tinha display=none para display=block.
```
window.addEventListener('mouseup', (e) => {
    drag = null;
    rotate = null;
    if (intersectionArea() > 0.95) {
        document.getElementById("myModal").style.display = "block";
    }
});
```

