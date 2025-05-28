-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               8.4.3 - MySQL Community Server - GPL
-- Server OS:                    Win64
-- HeidiSQL Version:             12.8.0.6908
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for studentid
CREATE DATABASE IF NOT EXISTS `studentid` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `studentid`;

-- Dumping structure for table studentid.admin_profiles
CREATE TABLE IF NOT EXISTS `admin_profiles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `position` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `fk_admin_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.admin_profiles: ~0 rows (approximately)

-- Dumping structure for table studentid.cars
CREATE TABLE IF NOT EXISTS `cars` (
  `id` int NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `model` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `year` int NOT NULL,
  `plate_number` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `seats` int NOT NULL,
  `engine_transmission` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `fuel_type` enum('Gas','Diesel','Electric','Hybrid') COLLATE utf8mb4_general_ci DEFAULT 'Gas',
  `image` varchar(255) COLLATE utf8mb4_general_ci DEFAULT 'default_car.jpg',
  `status` enum('available','rented','maintenance','damaged') COLLATE utf8mb4_general_ci DEFAULT 'available',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `rate_per_day` decimal(10,2) NOT NULL DEFAULT '0.00',
  `category` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.cars: ~8 rows (approximately)
INSERT INTO `cars` (`id`, `name`, `model`, `year`, `plate_number`, `seats`, `engine_transmission`, `fuel_type`, `image`, `status`, `created_at`, `rate_per_day`, `category`) VALUES
	(7, 'Toyota', 'Wigo', 2023, 'BSJ23', 4, 'moter', 'Diesel', '01_mini_white_1.png', 'rented', '2025-03-21 04:39:56', 400.00, 'popular'),
	(8, 'Volkswagen', 'Polo', 2025, '20356h', 6, 'hubmme', 'Electric', '40_hatchback_blue.png', 'rented', '2025-03-21 04:41:32', 6000.00, NULL),
	(10, 'Gusion', 'modelo', 768, 'nivv8vg', 4, 'hubmme', 'Electric', '850aca7cd77c110e99ab20862aef14cf.jpg', 'rented', '2025-03-21 05:11:36', 7000.00, NULL),
	(11, 'SUV', 'SUB', 2024, 'vshjhb4', 6, 'cdfsdg', 'Diesel', '01_mini_white_1.png', 'available', '2025-03-22 02:28:07', 2000.00, NULL),
	(12, 'Toyota Camry', 'Sedan', 2022, 'ABC123', 6, 'Automatic', 'Electric', '11452734.png', 'rented', '2025-03-22 02:54:59', 2000.00, 'popular'),
	(13, 'BMW X5', 'SUV', 2023, 'XYZ789', 6, 'Automatic', 'Diesel', '3d-car-with-simple-background.jpg', 'damaged', '2025-03-22 02:54:59', 5000.00, 'luxury'),
	(14, 'Honda CR-V', 'SUV', 2021, 'DEF456', 6, 'Automatic', 'Diesel', '02_economy_white.png', 'available', '2025-03-22 02:54:59', 3000.00, 'suv'),
	(15, 'Toyota Corolla', 'Sedan', 2020, 'GHI789', 4, 'Manual', 'Diesel', '11452734.png', 'rented', '2025-03-22 02:54:59', 1500.00, 'economy');

-- Dumping structure for table studentid.car_rentals
CREATE TABLE IF NOT EXISTS `car_rentals` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `car_id` int NOT NULL,
  `pickup_date` datetime NOT NULL,
  `return_date` datetime NOT NULL,
  `rate_per_day` decimal(10,2) NOT NULL DEFAULT '0.00',
  `subtotal` decimal(10,2) NOT NULL DEFAULT '0.00',
  `total` decimal(10,2) NOT NULL DEFAULT '0.00',
  `payment_method` enum('Cash','Credit Card','Bank Transfer','Online Payment') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `payment_reference` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `amount_paid` decimal(10,2) NOT NULL DEFAULT '0.00',
  `date_paid` datetime DEFAULT NULL,
  `signature` text COLLATE utf8mb4_general_ci,
  `qr_code` text COLLATE utf8mb4_general_ci,
  `status` enum('pending','approved','rejected','picked_up','returned') COLLATE utf8mb4_general_ci DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `extension_hours` int DEFAULT '0',
  `extension_fee` decimal(10,2) DEFAULT '0.00',
  `damage_fee` decimal(10,2) DEFAULT '0.00',
  `car_wash_fee` decimal(10,2) DEFAULT '0.00',
  `damage_description` text COLLATE utf8mb4_general_ci,
  `damage_photos` text COLLATE utf8mb4_general_ci,
  `contract_photos` text COLLATE utf8mb4_general_ci,
  `payment_provider` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.car_rentals: ~10 rows (approximately)
INSERT INTO `car_rentals` (`id`, `user_id`, `car_id`, `pickup_date`, `return_date`, `rate_per_day`, `subtotal`, `total`, `payment_method`, `payment_reference`, `amount_paid`, `date_paid`, `signature`, `qr_code`, `status`, `created_at`, `extension_hours`, `extension_fee`, `damage_fee`, `car_wash_fee`, `damage_description`, `damage_photos`, `contract_photos`, `payment_provider`) VALUES
	(8, 1, 7, '2025-03-22 00:00:00', '2025-03-28 00:00:00', 400.00, 2400.00, 2400.00, 'Online Payment', 'BOOKING-20250321-15NFOY', 2000.00, '2025-03-21 12:44:28', NULL, 'iVBORw0KGgoAAAANSUhEUgAAAXIAAAFyAQAAAADAX2ykAAAC2klEQVR4nO2bW4rrMAyGZcUwjynMAs5S3B3MkmZr9VK6gIH48YCLBsl2Lxmw3XNoJiH6H0pifQSBkCxfagiekcencADl68KGfS7l68KGfS7l68KGfS7l68KGfS7l98CbLAvgjU2vAHAxAKHYjgv60y98gt0x74g1yVMEOqWYv3HzNYiJ1u1/t3CnfMgZmlN3jEA0cf6mMbu0P73CbjJp97yjCObzzJX6MFCuyr/oT0PYAnbO2/mAP0xci6M1PP8ShGX9QeVfwo9EMuuCO0ulzrOu4fwlovi/3+8VdpNJynfxXubdgzwPBBAsmGOQ5L6k9vmR7xYqv4L6TLcB/+dvqcojZ+1Iq/Yfle9Z/x7TMtcC0fmNzFFCCxdDp2J44PuFyv8qD3eLW26dwU2Q1r8y69JJynWy8hS9Nv9R+bpIxGFMUT3dOi0iAjdxfGU5rPHdbv46yVWuypLEOaDxzqr5u0kecl5eszZtSEqRHrlwc6Rzudb4bo+35eFiCUbegA7vkr/WuInHeKXEBuNOa/Qfle/tryjPv/FhTh6lk87bHZq/W43vKNOsNFTcWnFX5VKQr6dLGt8N1+dgI5fmSF42sThr/WHi0vzFRfpQtkDW5j8q35e/sXTNsiASw5R/krR/3iIPZQWUa3HumlmuBD5111qft867NP/yrmRZFUE6bpAtzMX96RF2UfvlIeevNFRSi2WTI61/Y4F0/2qrPFxb43zNKvXPZcMK8o/Gd9P9s8lvQyQIA6ftQOBlNLzn12X8QeVf1l9RaZ1LuR5y/qaarfm75fkXrlG9P1MC0d12x9r8R+Wf473cmgz5fjtdDx5yO716/xvCvd+fhPEr3c8xji6Wr9vxGN/ZWcQfVP4l8R05fiHdxCLwH9FKQA2fJJH/+Ofvo/JrOT+C1CbfDvlB7nTkTkvXR5vkjf6/uyqsm39I+bqwYZ9L+bqwYZ9L+bqwYZ9L+bqwYYed89+bzfFBS7XBDgAAAABJRU5ErkJggg==', 'returned', '2025-03-21 04:44:28', 0, 0.00, 0.00, 0.00, NULL, NULL, NULL, NULL),
	(9, 1, 8, '2025-03-22 00:00:00', '2025-03-29 00:00:00', 6000.00, 42000.00, 42000.00, 'Cash', 'BOOKING-20250321-FPAYTO', 5000.00, '2025-03-21 13:05:00', NULL, 'iVBORw0KGgoAAAANSUhEUgAAAXIAAAFyAQAAAADAX2ykAAACyUlEQVR4nO1bXWrkMAyW5cA8JrAH6FEyNys90t4gOUpvED8OJGiRbCfTFGwPuzMbN/oeMnb0UQRC/6kheAQjPkQHUH4amJHvofw0MCPfQ/lpYEa+h/LTwIx8D+WfgW8CGoDRNGBMB2CusBhzdVF2faE+5cAHuGfkN/6nH/jpfgFAO/HJAAFYAnB2FoZ5jT6o/KfwXfTQfloMDS2ROK3IvGP/3d8vBRYzPZSfRvP9lSXD7koAS2P638fWH5X/GH/0vmrZfy9Un/4Z4En9t2VTOgDT0+KjMoHrDPE7OrD+qPwS/ijZtuOjuxD0k9TPlnwRvWbiw+pfDDyl/9J6p/HtFrx27Gx07Nfpg8r/p3wgBvQ0Aw3cEPXbtY2PDcPR9Efll8XnBqCnG4dhzr+uCZEa/EnnG1XzKTS8YlB+8PXdm1uSsCUaDqx/OfCs8Zm8VUOQnlgwhXDtTetPR9MflV863yCeSkp8Jr4Y4NQLrgPimaXOJ6vkQyicxGG9r9q13IJVarW+qpMP98VxzMRENPMk2nrTirk1PlfJh81r70zrV0fA5r4TqH3rra8m8VWpqsSqjFZaX2mC1b61+y+jjWFYrMoIlbTG57r55l389zMONMZui8+w7pRep0858AHumefPjn/am2HT8nFhgZ2lKzL+m46X6IPKf9b8GdYkLCf/zqMNIxCNzzX3R4xgRs7EgjDYiksGtW/l30/Sh+x6XRPWSeD3C5p/6+b34p1+q8/Y9gutBO5VcFD9i4En40OIyjHrhoWvr6ds2O3LuFLj80/gm6vvj8SqNxMaY3fhJeH/0CcHzDK+4ux8koGzbAo/ulg6j29zLfrngCf/ftKj/+Tvn92FDLTy3w1LQ8fUH5Vfkn8DxHXn4LUC6YS1P/o5309CvMV3vOTfbkfTH5WfBKbF36D8NDAj30P5aWBGvofy08CMfA/lp/Hs+uoPp8nhogKjFUIAAAAASUVORK5CYII=', 'returned', '2025-03-21 05:05:00', 0, 0.00, 0.00, 0.00, NULL, NULL, NULL, NULL),
	(10, 1, 10, '2025-03-29 00:00:00', '2025-04-24 00:00:00', 7000.00, 182000.00, 182000.00, 'Credit Card', 'BOOKING-20250321-L4EU2R', 10000.00, '2025-03-21 13:13:03', NULL, 'iVBORw0KGgoAAAANSUhEUgAAAXIAAAFyAQAAAADAX2ykAAACxUlEQVR4nO1bUaqjQBCsboV8KuQA7yh6s3emvUE8Sg6w4HwGlF66ZzTiLmpgX9DY9WHidBEamprpmpmQ4BU0/BIdcP4yeCU+h/OXwSvxOZy/DF6Jz+H8ZfBKfA7nn4FPCbl+y4GGiNCUANVhiNVvzGc7+AXuifmVKFpAbkUH+pZuZGQWkn3nvxl8Mn6ePkMJVL8AQgFIU7YCBIIg6Biybqf5s/M31XeAIOQdqrbPgeJ3vvv82fkv8osOca2t2kzSqvs/f38ZvBKfw/nb+IWI3LTTqoP1V5fJvofIcznea/5bwefkN9Yil8No1eoz2PTcx/b5vflsBm+nnpIPmeGGTKKcpf1HdG/5s/O3+N/atBqIUMW5uB8ML3oyJbv/PSQfU3EWHWwRNjtsnZa9Rk2bRXb9Hoyf25PUC0l1v0j0ug0lw0v6SlVb+vp7ZP3CZuWoUBtrkz8SbZ0Hiuv3qPoVhKsQwrVDJX2eRPz1IGlqbbeg2x1vyYed/xP6RaHz8fCwBTf1z7GJHtW9t/zZ+cuQiFY7KDtf0EGdrmO7NYl6fQ+sX5jr7cbSDlVFkVZn97/Hnp9lLGiSbjJJ4/6k6/e4fJFWtzGKByWva5UOpK8Ga7Lel8928Avc8/KJykyI9FShug+XOBIyQfN83Wf+28Fn9Ud5pwe+ScQItqGR6dbGVadmVfdb8mHn/4h+v3RqjgdGSc5WaTRlPz1Y2mn+28En42N2QBTHov+VZ5OVLmF5f3X0+5PQWtK3mHQzbbLyeBzs50eH5GOyuaz+aLhEOd3VQDLGrt/j1rcdDhS0tNEEy3grJ500eH0/gF/d04QMhMuo34f3z5/Bp9oubET06Zv6X19/P2X9zSa7zphsR/v8/AH3J0n1m5xwsJuygyd2/R6RT/7/7kXwcvgvOH8ZvBKfw/nL4JX4HM5fBq/E53D+MngljpPz/wBUeurHO6fJNgAAAABJRU5ErkJggg==', 'returned', '2025-03-21 05:13:03', 0, 0.00, 0.00, 0.00, NULL, NULL, NULL, NULL),
	(11, 3, 8, '2025-03-26 00:00:00', '2025-03-29 00:00:00', 6000.00, 18000.00, 18000.00, 'Cash', 'BOOKING-20250321-RGX6PG', 18000.00, '2025-03-21 13:17:04', NULL, 'iVBORw0KGgoAAAANSUhEUgAAAXIAAAFyAQAAAADAX2ykAAACtUlEQVR4nO1b0W3jMAwlaQH3aQMdIKMoG2SmGykb2KNkA/uzgAIWFKXk6itkJ0BSK+H7cGXzISBAPJKSWGS4BQPdRAcwfhm0YJ/D+GXQgn0O45dBC/Y5jF8GLdjnMP478DHBAQydlFlEBIAzAkzZtn+iP+tBN3DfmO9ZMMrq5PQTYtdI89VEE2/b/9WgN+VPSaGIuwC4bwMwn6KIo7rd1v1fC1rNfGE+s4h46BpOWfmX/SmASsYf8G58N//gjwjg++BQ6i/D9Fx/yPgPiW8rBVZiOexiqY2lFwD9EYA37D8Zfw1/iC1yl/or3E/pASLiiO/81SDjb0C//P1jysptyMJ+nj9k/AfEF/1RtAtN4GH3iayhhbNjmJLhzt8n4/8qH/LmtmHuVbABuFdDkFWqxLpF7rfmPxm/DFaMspJHDG2fAwp+lPjG7bDFt179+jEeU0kYx6Tk9BqtHEy/1edn0NcY6ajkVgz/pGuLb8X6BQ2oFtwk2KA5W5O06bfq86smoD+53CZLkAeUxyE4FfFz/CHjP2b/+4kxjOjHTk4lPwL6GFI95Lj798n4m8jPHFNzzMWXmtzm+qvdteXnCvmQY5kb5v5qGNNDYfW3Rj5cd0DX1lnhL4GPjZfpt2b+5NLVvkxt6P63V0u+SbL5nPr1C+l8Mu1/QybZ+VXt55MZea+bDqwgPSy+dd8fgSLdH+X9L0ji/hAV50uGzflPxi+DVbXxT5SuNllpBZcmy/rnl5ifBGjTSQf/vUxC+9Mf0++LzNcN3cggt/oc5+uGgzRd02XEY2v+k/HvmJ8UoOezA3+S11ZmOjbpPxn/pvlJBpALhTyQg9AGx8Nhs/6T8df0Vwmxq5KFbn2bfF2ot//WX9XHR/v/7iKobP4Pxi+DFuxzGL8MWrDPYfwyaME+h/HLoAU7vDn/C/qI1L9icMBVAAAAAElFTkSuQmCC', 'approved', '2025-03-21 05:17:04', 0, 0.00, 0.00, 0.00, NULL, NULL, NULL, NULL),
	(12, 3, 7, '2025-03-22 00:00:00', '2025-03-28 00:00:00', 400.00, 2400.00, 2400.00, 'Cash', 'BOOKING-20250321-I43S2K', 600.00, '2025-03-21 14:05:59', NULL, 'iVBORw0KGgoAAAANSUhEUgAAAXIAAAFyAQAAAADAX2ykAAAC1UlEQVR4nO2bbYrjMAyGJSXQny7MAeYozg32SEtv1hxlbhD/LKRokWz3IwuOw850k0bvj04aPxSBeGX5Y5BhiXpahAMYXxbNjE9lfFk0Mz6V8WXRzPhUxpdFM+NTGb8HHpNaAAiI2MEVEY8A2MlXVffCeOpFC9g98m3848/yGT4AwY0t99gwQmhHhtCMSuBr4iHjf4QP2aH+qwXs3AWZh2tMajL2P/1+raiajDJ+Id8fGwY/NIwoT9/++zOiOWAi48tqJ981owxwlYEr8trjJ+OreMfMOgf3x/SGRVqzmXlce/y1on3yvbbI0jD/1vk3HBi7oOaWThoR1x1/tWiX9ZnvL/qjtsrSWjlxreNVx0/G16x/O/2jhtVK7VjSekU+Sess7n7i60XG/1cedJoFgIYfnjS/XmZdr+8k56rz2uIn4yt4lg5K96r47C6oy2HNdPK0lusHvl5k/Dr8C8BnNwLzoE/6eoxP0cTyYf7dZn75ltrkWmmtvOY3Fu5UqS2/2+Sxy1nVTOv+VSbSScNL46kXLWB3zPu86r3PtXxC+aqLpHBIux9rjb9atM/6zFqaNZe5IMeJOTbRMmr1eYs8TNKoNk09l9OP3HPZ+miLPNxzmTIdp14x8ZDSHXsu8+/mz38DIp8+tTRfEPrPW7keXh5Praia3Hd9Hpqnbaq7nTmtnsy/255/RTrNSqbjTOxup4I6CYssvxvtn7PS1saQt6P9zd3m33e4P8naP6t1ez01imdKupP1unjqRQvYPfJwt6mW5lykZcE7JNfGlZL59y3uT/bSNeslO5CdrNvRr/n3Le7Xgf86MPrhA1huYqVd6ID5aW3xk/HL8tv/0qXvBcGzXKIMcrbgxnal8ZPxy+5P+oejoyQ+63W7VcdfK9rv+T48H/2mmzq6NZmXS9ZfbY1H+//uoqg8/JeML4tmxqcyviyaGZ/K+LJoZnwq48uimXHYOf8HHTDfduEQY9wAAAAASUVORK5CYII=', 'returned', '2025-03-21 06:05:59', 0, 0.00, 0.00, 0.00, NULL, NULL, NULL, NULL),
	(13, 3, 7, '2025-03-24 00:00:00', '2025-03-27 00:00:00', 400.00, 1200.00, 1200.00, 'Cash', 'BOOKING-20250321-9DCKWA', 2000.00, '2025-03-21 16:35:09', NULL, 'iVBORw0KGgoAAAANSUhEUgAAAXIAAAFyAQAAAADAX2ykAAACvklEQVR4nO1bbYrjMAx9VgL704U9wBzFvcGcdW6QHGUOsND8LLhokWy3mSw4KeyUeKL3o22qRxG8kfVhjWM8g5GeogPGr4NW7EsYvw5asS9h/Dpoxb6E8eugFfsSxj8C32X0AKY+PQK4OWAqtvML/dkOeoJ7YH5gwUUqqLcIHkTzMzopvjo18b793ww6GL/P79MJCB+AC58Suf5Pz/KdyuqALr7IHzL+9/LHE8D82cunjvOp/B9/fwW0RljA+Nvi947wcZL4jb2T/MuYsGv/yfib+J5Zs65Im1KvQuOXmePe/d8KOiZ/1BJZIhfTL05F9HnS4L6l8vm1/mwGbace+Hzm+VfSFSm8RK3nXftPxt+gr0tZF13k8aS1sh7It1REq2Gn/pPx62DFkBJunGVifVTDrEUe9uY/Gb8O1uFFEGnDBUtBES7y6GP5O9ib/2T8rfGLJLLOqpKg8Yv6pm/L+gI6n+TB3yPZF6XzcW36tsdHHi77EqaPT0HjV2bS+TvTt9n5VRhuvQ6hWapmvVXA6OTlPYqhj7xP/8n4dfAdj7M4VVWhHNz5dsnit/H8O0iTJFl3dmZDKy1Jx6Zvi3x8qZC1tOrm5RZr/hVY/m2ZP8mFoJPRc4E7e2bn9Lr/cfuwV/+3gg7K96KgvzrAX5073zMxyrjD9nOaPp8vZRdn3v/GQrL51Q+onxUq7WySFUp2TmbTt837IyTI/dGbnsfa/0IS82+J4jKT3p3/ZPw6OEWtvmnXu3jh3CRZ/dx2/kWeatwXYuc3SY9xx978J+M/yfdXp+s6usnxaI2sP/oZ+5OQ1atwOcEFvvXI69BXZ/PnpvX1ot+km1i6lZMXcpxsyvL4/jJ/yPjfkX8z8iV/mUp25eJfZpbWH7XId/b/3VVQ3fwPjF8HrdiXMH4dtGJfwvh10Ip9CePXQSt2HJz/F27c9/5EUCrgAAAAAElFTkSuQmCC', 'picked_up', '2025-03-21 08:35:09', 0, 0.00, 0.00, 0.00, NULL, NULL, NULL, NULL),
	(14, 1, 15, '2025-03-23 00:00:00', '2025-03-27 00:00:00', 1500.00, 6000.00, 6000.00, 'Cash', 'BOOKING-20250322-DHPYJN', 600.00, '2025-03-22 16:18:16', NULL, 'iVBORw0KGgoAAAANSUhEUgAAAXIAAAFyAQAAAADAX2ykAAAClElEQVR4nO1bUYrrMAwcK4F+pvAOsEdJj54cZW9Qfy4kaJFsJ20WHBf2LU6j+XCTaigCMbIluY7xCkZ6iQ4YPw/asW9h/Dxox76F8fOgHfsWxs+DduxbGP8MfBfRwt18i/gEyGuy3Sr2vxx0Mn4bPvpBVv8PDD87ALPj0UFem0kZrk7/yfhFfJ8UOn5MQH9vGOiYg4hFzht+Kcj4Neh3gQMuUjJpkOeW4VG1/2T8V/lz2mvRBP3+8u9nQXnzDxi/TL+diNbHnVj3Wl1Uv1yx/2T8Ev6oR+SrPPo2Lv1d9TuH4/Mzvxhk/Ar0y49fzQ7jx5fDeIXjja06/8n4JfXvLdW6uuvqwsOTsK3+PSQfrBi6CY9LCjIUPTPrwkNt/pPx82DBGkvmewoogohl6aRcsvgeW7/oeZL4NhyWYYkvq8Hie1z99ho8jeUdkp9VxBMeQmvxfRv9QsMtQC/pWmH5+cj7b6dTBO06h3lCPGT1wWrnq0PzOar2K7UxuikVRN65BxFX6n856Kz5mWPBK0laBavfrZk68mrzn4xflJ+hT0to19Qs0HGh5ecj9yf9VQYKDTt4JyJeGc3kdCb8N/6Q8f9HfmY5OmuSfq5/ITux5ec3OD9ziGrcf/X83C2qVavF97B81q5kKI38JYQS/eclbsJ2fn6b+5PAMvAdr3LTTibBo82P3qE/yWvXeWl39Gv2tvx84PjeUxkUm1hrTwtisP7km9yf5PDhnTzN8VXyM9fpPxn/Rb6Xq1fhEN0s8/2lXVm//3nQSfld6k+mq1ei2jmeufT1b/0pBRUzT52fxzBYaKSJ1Uo7a7lEOUSi5edD8p39vzsLypt/wPh50I59C+PnQTv2LYyfB+3YtzB+HrRjx8n53zaXz5ivckqhAAAAAElFTkSuQmCC', 'pending', '2025-03-22 08:18:16', 0, 0.00, 0.00, 0.00, NULL, NULL, NULL, NULL),
	(15, 1, 13, '2025-03-23 00:00:00', '2025-03-25 00:00:00', 5000.00, 10000.00, 10000.00, 'Cash', 'BOOKING-20250322-L7GD4K', 5000.00, '2025-03-22 17:36:15', NULL, 'iVBORw0KGgoAAAANSUhEUgAAAXIAAAFyAQAAAADAX2ykAAACxElEQVR4nO2bUW7bMAyGSVpAHm1gB8hR3BvsSL2adZTewH4sIIMDKSlZPEBysDW1Zv4PiR1+KAgQoihSRYZn5OkpHMD4sqhi38r4sqhi38r4sqhi38r4sqhi38r4M/CY5ABxWBE8IoIfAPBtyba3F/qzX/QEe2J+ZNEsj4vLtgWRJ+jUxMf2f7fopPxyW6G9xrJjGGdZv3F1u6P7v1d0cp4n+RxnSdLDAfypiarEo87O4/uHA/DXICs5fL8/NVGVODfv0ncvSXkBYAktAlwYxo8Lo9j4wP6T8Xt4ryXykNfvbesFgDWWz4/8bpHxB1i/fHtnP3TpCUCTNB/afzK+LNbDz8h5rx3n7iGivVjnfISajuY/GV8WR0lUYwT1wDt38gS5yOoTZfFtk0fUgllbG32A7UkYFtt/295//c/Vsb9+ShhdYFhW1CzNsLgA4/Qyf8j4r+Lx/eMiWVkK5kE34TU2OeJv1n9uub6atc0c5DXkdjTn0kpl9VXDvL9+Ir7J/hu7knHDXVG3Y5svNF8/T1I1T7Gg0oS8KafB1m/b56PHII+3TA2yfqe8iC2+rfGgYdNjkIYxh1Zi2WtoNdxZFt/GeMjxlad7VyPPf/k+37f83Dzf5/U79XIS7kOaNNh84X/gUernfFej43j/Sq9jfY8/u0T7sNPycNtaf0vDm6kCxFfLz832JzG9dQFg+SFl8+rkEodLr4v0LF/iDxn/tfcn/VX2X50qgHzE+ZE2pv/i7+8W7UdVxlfEMStrLtYhoTYk44E3JCZ1Ly0/t8e77Q9+0CSdfuf0G8Rx0vH8J+Of4jlecpes7GMlLaOj+0z46P7XRCfle+1P3kMr9ydnedWVvFxsvtAm7+KXj/VTJ5W05OeoLiD0waVJ/0v8IeP/KY/2/91FUdn8h4wviyr2rYwviyr2rYwviyr2rYwviyp2ODn/Cx5LqHjJudX4AAAAAElFTkSuQmCC', 'pending', '2025-03-22 09:36:15', 0, 0.00, 0.00, 0.00, NULL, NULL, NULL, NULL),
	(16, 5, 12, '2025-04-09 00:00:00', '2025-04-10 00:00:00', 2000.00, 2000.00, 2000.00, 'Online Payment', 'BOOKING-20250409-8H4FBL', 2000.00, '2025-04-09 19:39:58', NULL, 'iVBORw0KGgoAAAANSUhEUgAAAXIAAAFyAQAAAADAX2ykAAAC1UlEQVR4nO1bbYrjMAyVlMD8TKAH6FGSG+yReqa9QX2UPcBA/HPARYtkJdPNguPuMkPS6v1oE+tRDOJZXy4yPIJAD9EBnF8GbdjXcH4ZtGFfw/ll0IZ9DeeXQRv2NZz/Cnw0tICjvAdEhNAD4Bhn27jj/deDXozf5q/hKp/xBBywSTjwrYVhUlOT9Au/Zz/k/C/hR1MoXvhDpNuwipjF7yrs//z9WlA1M8P5ZbSrdw79JCXTrQXo3tvd75+c/xh/+DXH2mFq2KJugb8Bcv4u9NuJaKOE2S61EoRZAy7LGu94/+T8Gn7QFLlX/b4xXjS1ippO33L6/Ce/GuT8HeiXl3cOfQMczilLF7Kwv28/5PyvqH/HKI6OJtOs2hFukj/fcFbyv/9+PegBrsD5dfwuAeI5l7o5tQIRMQQpjaTTseLXgpy/i/wqnhKHsQUYWA5p/OxqNAmHqff4e0w+sAAGTvKUgK9dEv2aiFnXjMLM173tn5xfBiuunXzoQidOhkbWkj2Jk92/h+RDFmdGZ0qWrjMzT2LVD/fvsfmcj+Y5f2bWJvQ5mc8hvvGu918Pes3zmSVhzr4Ee7pbs+js+j0eH8xv8iSxVlMrS7LYDm4/n5+g/zxJ6/kdJb9qcZiAEWIPHHJbw9rR+9s/Ob/CvwidDPR/ttKp1NGv1b+g8/3wY9rr/sn5Vf3nKA9daiGMnw2NRp5OUgnLOHiX+yfn19VHzX1qlSMxLxqew7HH3wPPj3hZtNHvfDELvT56mvuToEOkYbmEBXJwS07t86ND8uGuuSwFr1VKWvVOekjL6e3n89H9Oy0DBU2VpfXMS/y1SYP79wn4oTcR566k6ffD54PPwcdRfanlEsjVDYEM+T3+Pkv8baxSGnJXUmfCdjz7+Xz0+5N4UYfqYpSrOfNfF1y/h+Sj/7+7CCqb/4Lzy6AN+xrOL4M27Gs4vwzasK/h/DJoww4vzv8NYv2cMKYXU+wAAAAASUVORK5CYII=', 'pending', '2025-04-09 11:39:58', 0, 0.00, 0.00, 0.00, NULL, NULL, NULL, 'Bank Transfer'),
	(17, 8, 10, '2025-04-11 00:00:00', '2025-04-18 00:00:00', 7000.00, 49000.00, 49000.00, 'Cash', 'BOOKING-20250410-Z3F4FE', 800.00, '2025-04-10 22:00:50', NULL, 'iVBORw0KGgoAAAANSUhEUgAAAXIAAAFyAQAAAADAX2ykAAAC1ElEQVR4nO1aXYrjMAyW1MA+OrAH6FGSmw17s+Qoc4CB+LGQoEWy07TeXSdlacdp9D24sfVRBEKyfowMj6Cnh+gAxs+DVuQpjJ8HrchTGD8PWpGnMH4etCJPYfwj8DGiAmy9LDChLgB+lrUv1Gc76AHuEflV+Gk6Wf1PAHAXZPA1cF8PknydRmXga/Qh4z+F76OH8q9a0mRZms94po79n/+/FbSZGWD8PKpkj+AAsOHosAy+bP3J+A/xuYMTq/+yhOx46/6bvwYyfhH+6+SqVV/11ciyQMNTpf7LBetPxt/C7zVFrgHwY4hei63/wSGTFtzzN4OM/6184HvMxyfWSJ2iK01/Mv6W+rf1iOrEzIOaVs7cBbUchr7WcnjhbwcZv4D7l8FLmeu+5nKYtbVRiUC+ljS7NP3J+HlwiMqOGZrhpA0N+Zoz6Uaj8jVSW3zeqX0V7nrNqmCYl24RlKY/GX8T34mR5a7VRbwWW8eMeJb2pNzO9/ytIOOX4L/NIN9uvHXYTo4kZutZjNSl6U/Gz4MjxtCw4i4YebYquFFMq4vZd8f37ynkUmrLaGTWrdW/71AfwST1bzzEZpAjL1MkmCoAN7xKHzL+M+JztyRZ4rohYR6k07FszX93yIclDMeDcOHGqhdCzmXxea98iIYLGbI+1dCbOH7xtQi2/GqX/Cr89C0AX+9f7usv+Z3CAcojHXuf8ybzI3fbv4Jr4Lb4/BbvJyG8upJMq9f0WXtar9ZnO+gB7hH5cFvm6nxhzq9CT2upic1/996fbEJBtFiabwYPll+9BR/DpL+ekDuZ/0rjUmN2LJFL138NtMo4AB8/gv9exNLyJvos46Tv0ycDygn/gqO/n2Td9ecLQvNZxefQ4OQl5Uv0IeM/Z74AN62NME4SzKMjy6/2Pl+IYDVyXCDdlqc/GT8Lyov/gPHzoBV5CuPnQSvyFMbPg1bkKYyfx7Pzq998rQnBsETy7gAAAABJRU5ErkJggg==', 'pending', '2025-04-10 14:00:50', 0, 0.00, 0.00, 0.00, NULL, NULL, NULL, NULL);

-- Dumping structure for table studentid.car_status_history
CREATE TABLE IF NOT EXISTS `car_status_history` (
  `id` int NOT NULL,
  `car_id` int NOT NULL,
  `status` enum('available','rented','maintenance','damaged') COLLATE utf8mb4_general_ci NOT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime DEFAULT NULL,
  `notes` text COLLATE utf8mb4_general_ci,
  `created_by` int NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.car_status_history: ~3 rows (approximately)
INSERT INTO `car_status_history` (`id`, `car_id`, `status`, `start_date`, `end_date`, `notes`, `created_by`, `created_at`) VALUES
	(1, 13, 'damaged', '2025-03-23 17:31:00', '2025-03-27 17:34:00', 'Na guba kay naka disgrasya', 2, '2025-03-23 09:34:26'),
	(2, 13, 'damaged', '2025-03-24 18:54:00', '2025-03-26 18:55:00', '', 2, '2025-03-23 10:55:22'),
	(3, 13, 'damaged', '2025-04-09 19:42:00', '2025-04-11 19:42:00', 'Damage', 2, '2025-04-09 11:42:54');

-- Dumping structure for table studentid.daily_sales
CREATE TABLE IF NOT EXISTS `daily_sales` (
  `id` int NOT NULL,
  `date` date NOT NULL,
  `total_rentals` int NOT NULL DEFAULT '0',
  `total_amount` decimal(10,2) NOT NULL DEFAULT '0.00',
  `extension_fees` decimal(10,2) NOT NULL DEFAULT '0.00',
  `damage_fees` decimal(10,2) NOT NULL DEFAULT '0.00',
  `car_wash_fees` decimal(10,2) NOT NULL DEFAULT '0.00',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.daily_sales: ~0 rows (approximately)

-- Dumping structure for table studentid.expenses
CREATE TABLE IF NOT EXISTS `expenses` (
  `id` int NOT NULL,
  `date` date NOT NULL,
  `category` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `description` text COLLATE utf8mb4_general_ci NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `receipt_photo` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_by` int NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.expenses: ~0 rows (approximately)

-- Dumping structure for table studentid.payment_providers
CREATE TABLE IF NOT EXISTS `payment_providers` (
  `id` int NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `description` text COLLATE utf8mb4_general_ci,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.payment_providers: ~5 rows (approximately)
INSERT INTO `payment_providers` (`id`, `name`, `description`, `is_active`, `created_at`) VALUES
	(1, 'Cash', 'Cash payment at office', 1, '2025-03-22 15:49:09'),
	(2, 'Credit Card', 'Credit card payment', 1, '2025-03-22 15:49:09'),
	(3, 'Bank Transfer', 'Bank transfer payment', 1, '2025-03-22 15:49:09'),
	(4, 'GCash', 'GCash mobile wallet', 1, '2025-03-22 15:49:09'),
	(5, 'PayMaya', 'PayMaya mobile wallet', 1, '2025-03-22 15:49:09');

-- Dumping structure for table studentid.pricing_settings
CREATE TABLE IF NOT EXISTS `pricing_settings` (
  `id` int NOT NULL,
  `setting_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `setting_value` decimal(10,2) NOT NULL,
  `description` text COLLATE utf8mb4_general_ci,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.pricing_settings: ~5 rows (approximately)
INSERT INTO `pricing_settings` (`id`, `setting_name`, `setting_value`, `description`, `updated_at`) VALUES
	(1, 'extension_hour_rate', 100.00, 'Rate per hour for extending rental beyond return date', '2025-03-22 15:49:09'),
	(2, 'car_wash_fee', 300.00, 'Standard car wash fee', '2025-03-22 15:49:09'),
	(3, 'minor_damage_fee', 1000.00, 'Fee for minor damages', '2025-03-22 15:49:09'),
	(4, 'moderate_damage_fee', 5000.00, 'Fee for moderate damages', '2025-03-22 15:49:09'),
	(5, 'major_damage_fee', 10000.00, 'Fee for major damages', '2025-03-22 15:49:09');

-- Dumping structure for table studentid.students
CREATE TABLE IF NOT EXISTS `students` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` varchar(11) COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `course` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `contact` varchar(15) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `guardian_name` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `address` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `barcode` text COLLATE utf8mb4_general_ci,
  `profile_picture` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `phone` varchar(15) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `application_status` enum('pending','processing','done','receive') COLLATE utf8mb4_general_ci DEFAULT 'pending',
  `signature` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`),
  UNIQUE KEY `student_id_2` (`student_id`),
  UNIQUE KEY `student_id_3` (`student_id`),
  CONSTRAINT `fk_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`student_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.students: ~2 rows (approximately)
INSERT INTO `students` (`id`, `student_id`, `name`, `course`, `contact`, `guardian_name`, `address`, `barcode`, `profile_picture`, `phone`, `application_status`, `signature`) VALUES
	(58, '22000444000', 'Ruperto Bernales', 'BSBA-Financial Management', '09504274037', 'Marian Bernales', 'P-8B Ambago,Butuan City', '22000444000.png', 'ID_face_.png', NULL, 'done', '22000444000_signature.png'),
	(59, '21000362700', 'Charnelyn Estal', 'BS in COMPUTER SCIENCE', '09463293862', 'Mahal', 'Libertad ', '21000362700.png', '142207-phones-feature-what-is-apple-face-id-and-how-does-it-work-image1-5d72kjh6lq.jpg', NULL, 'pending', '21000362700_signature.png');

-- Dumping structure for table studentid.student_history
CREATE TABLE IF NOT EXISTS `student_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` varchar(11) COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `course` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `contact` varchar(15) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `guardian_name` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `address` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `profile_picture` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `signature` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `barcode` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `received_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.student_history: ~0 rows (approximately)

-- Dumping structure for table studentid.support_messages
CREATE TABLE IF NOT EXISTS `support_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` varchar(11) COLLATE utf8mb4_general_ci NOT NULL,
  `subject` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `message` text COLLATE utf8mb4_general_ci NOT NULL,
  `status` enum('pending','in_progress','resolved') COLLATE utf8mb4_general_ci DEFAULT 'pending',
  `admin_response` text COLLATE utf8mb4_general_ci,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `is_seen` tinyint(1) DEFAULT '0',
  `auto_reply` text COLLATE utf8mb4_general_ci,
  PRIMARY KEY (`id`),
  KEY `fk_support_student` (`student_id`),
  CONSTRAINT `fk_support_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`student_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.support_messages: ~2 rows (approximately)
INSERT INTO `support_messages` (`id`, `student_id`, `subject`, `message`, `status`, `admin_response`, `created_at`, `updated_at`, `is_seen`, `auto_reply`) VALUES
	(14, '22000444000', 'Update', 'Hi sir maki update lang ko', 'in_progress', NULL, '2025-04-20 13:20:04', '2025-04-20 15:03:14', 0, 'Thank you for requesting an update. Our team will review your inquiry and provide you with the latest information as soon as possible. For faster assistance, please specify which matter you need an update on.'),
	(15, '21000362700', 'Random questions', 'Are u gay?', 'in_progress', NULL, '2025-04-20 13:40:36', '2025-04-20 14:50:31', 0, 'Thank you for your message. Our support team will review your inquiry and respond as soon as possible. Please check back later for updates.');

-- Dumping structure for table studentid.support_message_history
CREATE TABLE IF NOT EXISTS `support_message_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `message_id` int NOT NULL,
  `response_by` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `responder_role` enum('student','admin') COLLATE utf8mb4_general_ci NOT NULL,
  `response` text COLLATE utf8mb4_general_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_seen` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `fk_history_message` (`message_id`),
  CONSTRAINT `fk_history_message` FOREIGN KEY (`message_id`) REFERENCES `support_messages` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=154 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.support_message_history: ~22 rows (approximately)
INSERT INTO `support_message_history` (`id`, `message_id`, `response_by`, `responder_role`, `response`, `created_at`, `is_seen`) VALUES
	(132, 14, '22000444000', 'student', 'Update lang ko sir', '2025-04-20 13:20:31', 1),
	(133, 14, 'ADMIN_17', 'admin', 'about sa?\r\n', '2025-04-20 13:20:43', 0),
	(134, 14, 'ADMIN_17', 'admin', 'sa?\r\n', '2025-04-20 13:22:02', 0),
	(135, 14, '22000444000', 'student', 'Sir', '2025-04-20 13:25:24', 1),
	(136, 14, 'ADMIN_17', 'admin', 'yes don?', '2025-04-20 13:25:44', 0),
	(137, 14, 'ADMIN_17', 'admin', 'hahahaha', '2025-04-20 13:28:04', 0),
	(138, 14, '22000444000', 'student', 'Katawa man ka kol?', '2025-04-20 13:28:55', 1),
	(139, 14, 'ADMIN_17', 'admin', 'bawal dong?', '2025-04-20 13:29:18', 0),
	(140, 14, '22000444000', 'student', 'Wala kay buot kol', '2025-04-20 13:30:39', 0),
	(141, 14, 'ADMIN_17', 'admin', 'ali be kay bagon ulo\r\n', '2025-04-20 13:31:00', 0),
	(142, 14, 'ADMIN_17', 'admin', 'hahaha', '2025-04-20 13:32:17', 0),
	(143, 14, '22000444000', 'student', 'Yawa jd ka ba', '2025-04-20 13:32:59', 0),
	(144, 14, 'ADMIN_17', 'admin', 'bahoo', '2025-04-20 13:33:26', 0),
	(145, 14, 'ADMIN_17', 'admin', 'gdfgdfgd', '2025-04-20 13:36:08', 0),
	(146, 15, 'ADMIN_17', 'admin', 'no', '2025-04-20 13:40:57', 0),
	(147, 14, '22000444000', 'student', 'Send', '2025-04-20 13:41:44', 0),
	(148, 15, '21000362700', 'student', 'Buttaasss', '2025-04-20 13:41:44', 0),
	(149, 15, 'ADMIN_17', 'admin', 'fsfsdfs', '2025-04-20 13:50:12', 0),
	(150, 14, 'ADMIN_17', 'admin', 'fsfsfsfsdf', '2025-04-20 13:50:20', 0),
	(151, 15, 'ADMIN_17', 'admin', 'dfsdfs', '2025-04-20 14:50:31', 0),
	(152, 14, 'ADMIN_17', 'admin', 'fsdfsss', '2025-04-20 15:03:08', 0),
	(153, 14, 'ADMIN_17', 'admin', 'fsfstertrhyjyuuy', '2025-04-20 15:03:14', 0);

-- Dumping structure for table studentid.users
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` varchar(11) COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `role` enum('student','admin') COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'student',
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`),
  UNIQUE KEY `student_id_2` (`student_id`),
  KEY `idx_student_id` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.users: ~1 rows (approximately)
INSERT INTO `users` (`id`, `student_id`, `name`, `password`, `role`) VALUES
	(17, 'admin001', 'Admin User', 'scrypt:32768:8:1$3gmDQCDyhijiMdn4$c812f2cc2e0b8e7733090ecdf81b9576782af57ab517a7519eb2ba9d416da9fefbc5e4eeffc48249936d4473e1b1c9d7ae1f049b876bb8b14cc6165426d0cc19', 'admin'),
	(63, '22000444000', 'Ruperto Bernales', 'pbkdf2:sha256:600000$4HCMPcEyq15K2SiA$2da1f494f75c6810746a4d79c930f0c1fea01f6bf006494e1efe5f78958466a4', 'student'),
	(64, '21000362700', 'Charnelyn Estal', 'pbkdf2:sha256:600000$jmC0GoPutCSHfwPW$e0ef16cb446edc7f908675fc5ec9d8594e9afee8e2e93fa9134bb1159eeb6697', 'student');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
