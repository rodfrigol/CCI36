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

### Rotate com mousewheel

### Rotate suave com mouse2

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
