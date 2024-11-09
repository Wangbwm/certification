/*
 Navicat Premium Data Transfer

 Source Server         : MySQL_192.168.198.100
 Source Server Type    : MySQL
 Source Server Version : 50742
 Source Host           : 192.168.198.100:3306
 Source Schema         : certification

 Target Server Type    : MySQL
 Target Server Version : 50742
 File Encoding         : 65001

 Date: 09/11/2024 11:38:35
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for sys_approve
-- ----------------------------
DROP TABLE IF EXISTS `sys_approve`;
CREATE TABLE `sys_approve`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `room_id` int(11) NOT NULL,
  `manager_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `pro_status` tinyint(4) NOT NULL,
  `app_status` tinyint(255) NOT NULL,
  `create_time` datetime(0) NOT NULL,
  `notes` longtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `room_id`(`room_id`) USING BTREE,
  INDEX `sys_approve_ibfk_1`(`manager_id`) USING BTREE,
  INDEX `sys_approve_ibfk_2`(`user_id`) USING BTREE,
  CONSTRAINT `room_id` FOREIGN KEY (`room_id`) REFERENCES `sys_room` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `sys_approve_ibfk_1` FOREIGN KEY (`manager_id`) REFERENCES `sys_manager` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `sys_approve_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_approve
-- ----------------------------
INSERT INTO `sys_approve` VALUES (1, 1, 1, 2, 1, 1, '2024-11-09 03:14:17', NULL);
INSERT INTO `sys_approve` VALUES (2, 1, 1, 4, 1, 1, '2024-11-09 03:16:18', NULL);

-- ----------------------------
-- Table structure for sys_manager
-- ----------------------------
DROP TABLE IF EXISTS `sys_manager`;
CREATE TABLE `sys_manager`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `telephone` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `address` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `sys_manager_ibfk_1`(`user_id`) USING BTREE,
  INDEX `sys_manager_ibfk_2`(`telephone`) USING BTREE,
  CONSTRAINT `sys_manager_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `sys_manager_ibfk_2` FOREIGN KEY (`telephone`) REFERENCES `sys_user` (`telephone`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_manager
-- ----------------------------
INSERT INTO `sys_manager` VALUES (1, 2, '101', '涪城区');

-- ----------------------------
-- Table structure for sys_open
-- ----------------------------
DROP TABLE IF EXISTS `sys_open`;
CREATE TABLE `sys_open`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `room_id` int(11) NOT NULL,
  `room_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `pro_status` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `open_status` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `create_time` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `sys_open_ibfk_1`(`room_id`) USING BTREE,
  INDEX `sys_open_ibfk_2`(`room_name`) USING BTREE,
  CONSTRAINT `sys_open_ibfk_1` FOREIGN KEY (`room_id`) REFERENCES `sys_room` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `sys_open_ibfk_2` FOREIGN KEY (`room_name`) REFERENCES `sys_room` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_open
-- ----------------------------

-- ----------------------------
-- Table structure for sys_role
-- ----------------------------
DROP TABLE IF EXISTS `sys_role`;
CREATE TABLE `sys_role`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `create_time` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_role
-- ----------------------------
INSERT INTO `sys_role` VALUES (1, '用户管理员', '2024-11-07 14:54:52');
INSERT INTO `sys_role` VALUES (2, '自有员工', '2024-11-08 08:46:23');
INSERT INTO `sys_role` VALUES (3, '三方人员', '2024-11-08 08:46:38');

-- ----------------------------
-- Table structure for sys_room
-- ----------------------------
DROP TABLE IF EXISTS `sys_room`;
CREATE TABLE `sys_room`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `address` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `manager_id` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `manager_id`(`manager_id`) USING BTREE,
  INDEX `name`(`name`) USING BTREE,
  CONSTRAINT `manager_id` FOREIGN KEY (`manager_id`) REFERENCES `sys_manager` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_room
-- ----------------------------
INSERT INTO `sys_room` VALUES (1, '涪城区', '测试机房1', 1);
INSERT INTO `sys_room` VALUES (2, '游仙区', '测试机房2', 1);

-- ----------------------------
-- Table structure for sys_user
-- ----------------------------
DROP TABLE IF EXISTS `sys_user`;
CREATE TABLE `sys_user`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `telephone` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `create_time` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `telephone`(`telephone`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_user
-- ----------------------------
INSERT INTO `sys_user` VALUES (1, 'admin', '$2b$12$s3zl2zIROwv3HmQSwCu/d.sJgRo5iWT8YGbuEBinZJMdyOxQoMOZS', '123', '2024-11-07 11:12:35');
INSERT INTO `sys_user` VALUES (2, '测试账号1', '$2b$12$6oC2IIddmgM.OuIYgp0gLOVEN2AOSpHiklJjTyW8KW4fHJQzhPsJW', '101', '2024-11-08 00:54:50');
INSERT INTO `sys_user` VALUES (4, '测试账号2', '$2b$12$YWriB7TjdEWYvX7CoikrGew4V3NML5w.3Vxvpv2OdnVv.MCAbRLxC', '102', '2024-11-08 07:08:27');

-- ----------------------------
-- Table structure for sys_user_role
-- ----------------------------
DROP TABLE IF EXISTS `sys_user_role`;
CREATE TABLE `sys_user_role`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `sys_user_role_ibfk_1`(`user_id`) USING BTREE,
  INDEX `sys_user_role_ibfk_2`(`role_id`) USING BTREE,
  CONSTRAINT `sys_user_role_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `sys_user_role_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_user_role
-- ----------------------------
INSERT INTO `sys_user_role` VALUES (1, 1, 1);
INSERT INTO `sys_user_role` VALUES (2, 2, 2);
INSERT INTO `sys_user_role` VALUES (3, 4, 3);

SET FOREIGN_KEY_CHECKS = 1;
