# CCI36

### Point-in-polygon

Para identificar se o cursor do mouse está sobre algum polígono usamos a função ```intersectObjects``` do three.js.
```
let intersects = raycaster.intersectObjects(children);
let aux = null;
if (intersects.length > 0) {
    aux = intersects[0].object;
}
```
Através do código acima conseguimos, dentre os objetos que estão sobre o mouse, selecionar o que está mais acima.

### Renderização de objetos dinâmicos

### Renderização de objetos estáticos

### Drag suave e com limites

Dentro do event listener mousedown, caso o botão clicado seja o principal, atribuimos à variável drag o objeto selecionado e salvamos os parâmetros drag.deltaX e drag.deltaY de acordo com a posição que o objeto foi clicado.
```
if (event.button === 0 && rotate === null) {
    drag = selected;
    drag.deltaX = drag.point.x - drag.object.position.x;
    drag.deltaY = drag.point.y - drag.object.position.y;
}
```
Após isso dentro do event listener pointermove a posição que o objeto ficaria de acordo com a posição final do pointer.
```let auxX = pointer.x - drag.deltaX, auxY = pointer.y * maxY - drag.deltaY;```
Após isso é feita a verificação se o objeto está dentro dos limites da tela. Caso esteja fora a posição é definida dentro dos limites, caso esteja dentro do limite a posição calculada é atribuida ao objeto.
```
drag.object.position.x = auxX < -1 ? -1 : auxX > 1 ? 1 : auxX;
drag.object.position.y = auxY < -maxY ? -maxY : auxY > maxY ? maxY : auxY;
```


### Rotate com mousewheel

Dentro do event listener mousewhell verificamos se não estamos selecionando nenhum objeto para arrastar. Então, escolhemos o objeto mais ao topo se o pointer estiver sobre mais de um objeto. Após isso rotacionamos o objeto de acordo com a rotação do mousewhell ```aux.object.rotation.z -= e.wheelDelta / 2000;```

### Rotate suave com mouse2

Dentro do event listener mousedown, se o botão clicado não for o principal acionamos o rotate.
```
else if (event.button !== 0 && drag === null) {
    rotate = selected;
    rotate.initial = Math.atan((rotate.point.y - rotate.object.position.y)/(rotate.point.x - rotate.object.position.x)) - rotate.object.rotation.z;
}
```
Dentro do event listener pointermove verificamos se ```rotate != null``` e rotacionamos o objeto de acordo com a posição do mouse.
```rotate.object.rotation.z = Math.atan((pointer.y * maxY - rotate.object.position.y)/((pointer.x - rotate.object.position.x))) - rotate.initial;```

### Função de cálculo de área (Polygon-intersection-area)

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

### Transformações geométricas 2D
