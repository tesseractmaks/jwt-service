
export function anyIelements(tagname, faClass, textPart1="") {
    let any = document.createElement(tagname)
    any.textContent = textPart1
    let i = document.createElement("i")
    i.classList.add("fa")
    i.classList.add(faClass)
    any.prepend(i)
    return any
};

export function pIelements(faClass, textPart1="") {
    let p = document.createElement("p")
    p.textContent = textPart1
    let i = document.createElement("i")
    i.classList.add("fa")
    i.classList.add(faClass)
    p.prepend(i)
    return p
};

export function aIelements(link, faClass, textPart1="", textPart2="") {
    let a = document.createElement("a")
    a.href = link
    let i = document.createElement("i")
    i.classList.add("fa")
    i.classList.add(faClass)
    a.textContent = textPart1 + textPart2
    a.prepend(i)
    return a
};

export function aElements(link, classes = [], textPart1="", textPart2="") {
    let node = document.createElement("a")
    
    if (classes.length) {
        node.classList.add(...classes)
    }
    
    node.href = link
    node.textContent = textPart1 + textPart2
    return node
};

export function Ielement(faClass, textPart1="", textPart2="") {
    let i = document.createElement("i")
    i.classList.add("fa")
    i.classList.add(faClass)
    i.textContent = textPart1 + textPart2
    return i
};

export function ulAelement(ulClass="", collection=[]) {
    let ul = document.createElement("ul")
    ul.classList.add(ulClass)

    collection.forEach(function (element, index) {
        let li = document.createElement("li")
        let a = document.createElement("a")
        a.href = element["link"]
        a.textContent = element["text"]
        li.append(a)
        ul.append(li)

    });
    return ul
};

export function anyElement(tag, classes = [], content) {
    const node = document.createElement(tag)

    if (classes.length) {
        node.classList.add(...classes)
    }

    if (content) {
        node.textContent = content
    }
    return node
};

export async function buttonElement(content, classes = [], idElem) {
    const button = document.createElement("button")

    if (classes.length) {
        button.classList.add(...classes)
    }

    if (content) {
        button.textContent = content
    }

    if (idElem) {
        button.id = idElem
    }

    return button
}

export async function imgElement(src, alt) {
    const img = document.createElement("img")

    if (src) {
        img.src = src
    }

    if (alt) {
        img.alt = alt
    }

    return img
}