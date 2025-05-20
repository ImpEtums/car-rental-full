import log4js from 'log4js';

const logger = log4js.getLogger('Order');

// 模拟车辆和订单数据
let cars = [
  { id: 1, name: 'Toyota Camry', price: 50, stock: 5 },
  { id: 2, name: 'Honda Accord', price: 45, stock: 3 }
];

let orders = [];

export const getCars = (req, res) => {
  logger.info('用户请求车辆列表');
  res.json(cars);
};

export const createOrder = (req, res) => {
  const { carId, days } = req.body;
  const userId = req.user.userId;

  const car = cars.find(c => c.id === carId);
  if (!car || car.stock <= 0) {
    logger.error(`用户 ${userId} 租车失败，车辆 ${carId} 无库存`);
    return res.status(400).json({ message: '车辆无库存' });
  }

  car.stock--; // 减少库存
  const order = { id: orders.length + 1, userId, carId, days, total: car.price * days };
  orders.push(order);

  logger.info(`用户 ${userId} 创建订单 ${order.id}`);
  res.status(201).json(order);
};

export const getOrders = (req, res) => {
  const userId = req.user.userId;
  const userOrders = orders.filter(o => o.userId === userId);
  res.json(userOrders);
};