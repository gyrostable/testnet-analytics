const findIntersect = (...array) =>
  array.reduce((acc, data) => data.filter((el) => acc.includes(el)), array[0]);

module.exports = findIntersect;
