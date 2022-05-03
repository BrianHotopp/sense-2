// implements a simple Queue data structure
export class Queue {
  constructor(...elements) {
    // Initializing the queue with given arguments
    this.elements = [...elements];
  }
  // Proxying the push/shift methods
  push(...args) {
    return this.elements.push(...args);
  }
  shift(...args) {
    return this.elements.shift(...args);
  }
  // proxying the map method
  map(...args) {
    return this.elements.map(...args);
  }
  // Add some length utility methods
  get length() {
    return this.elements.length;
  }
  set length(length) {
    return (this.elements.length = length);
  }
}
export function togglePush(q, el) {
  // write this better
  const i = q.elements.map((el) => el.id).indexOf(el.id);
  if (i > -1) {
    q.elements.splice(i, 1);
  } else {
    q.elements.push(el);
  }
}
export function shiftPush(q, el, thresh) {
  // push the new element if it is not already in the queue
  if (q.map((el) => el.id).indexOf(el.id) < 0) {
    // if there are more than thresh elements in the queue, remove the first one
    if (q.length >= thresh) {
      q.shift();
    }
    q.push(el);
  }
}
