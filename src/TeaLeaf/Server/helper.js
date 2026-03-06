class LocalState {
  constructor(init_val) {
    this.id = "";
    this.val = init_val;
    this._nodes = [];
    document.addEventListener("DOMContentLoaded", () => {
      this._render(null, init_val);
    });
  }

  set(data) {
    const old = this.val;
    this.val = data;
    this._render(old, this.val);
  }

  get() {
    return this.val;
  }

  _render(old, val) {
    if (this._nodes.length === 0) {
      const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
      );
      let node;
      const tag = `{{${this.id}}}`;
      while ((node = walker.nextNode())) {
        if (node.nodeValue.includes(tag)) {
          this._nodes.push(node);
          node.nodeValue = node.nodeValue.replaceAll(tag, val);
        }
      }
    } else {
      for (let node of this._nodes) {
        node.nodeValue = node.nodeValue.replaceAll(old, val);
      }
    }
  }
}

class Store {
  constructor(store_id) {
    this.store_id = store_id;
    this.base_url = "/api/_store/" + store_id;
  }

  async _apiCall(method, id, body) {
    let config = {
      method: method,
    };
    let url = this.base_url;
    if (id != undefined) {
      url = url + "/" + id;
    }
    if (body != undefined) {
      config.body = typeof body == "string" ? body : JSON.stringify(body);
    }
    let result = await fetch(url, config);
    if (result.ok) {
      const content = await result.text();
      for (let item of document.getElementsByClassName(
        this.store_id + id + "_react",
      )) {
        item.innerText = content;
      }
      fetch_front();
    }
    return result;
  }
  async suscribe(callback) {}
  async set(id, data) {
    await this._apiCall("POST", id, data);
  }
  async delete(id) {
    await this._apiCall("DELETE", id);
  }
  async update(id, data) {
    await this._apiCall("PATCH", id, data);
  }
  async get(id) {
    await this._apiCall("GET", id);
  }
}

async function fetch_front() {
  let result = await fetch(window.location.href);
  if (result.ok) {
    let serverHtml = await result.text();
    let vdom = new DOMParser().parseFromString(serverHtml, "text/html");
    authority_zero(vdom.body, document.body);
  }
}

function authority_zero(a, b) {
  if (a.children == undefined) {
    b.innerHTML = a.innerHTML;
    return;
  }
  for (const [vdom, dom] of zip(a.children, b.children)) {
    if (vdom.isEqualNode(dom)) continue;
    if (vdom.children.length == 0) {
      dom.innerHTML = vdom.innerHTML;
      for (const attr of vdom.attributes) {
        if (dom.getAttribute(attr.name) !== attr.value) {
          dom.setAttribute(attr.name, attr.value);
        }
      }

      for (const attr of [...dom.attributes]) {
        if (!vdom.hasAttribute(attr.name)) {
          dom.removeAttribute(attr.name);
        }
      }
    } else {
      authority_zero(vdom, dom);
    }
  }

  if (a.children.length > b.children.length) {
    //add elements
    for (let i = b.children.length; i < a.children.length; i++) {
      b.appendChild(a.children[i]);
    }
  } else if (a.children.length < b.children.length) {
    for (let i = b.children.length - 1; i > a.children.length - 1; i--) {
      b.removeChild(b.children[i]);
    }
  }
}

function* zip(a, b) {
  const len = Math.min(a.length, b.length);

  for (let i = 0; i < len; i++) {
    yield [a[i], b[i]];
  }
}
