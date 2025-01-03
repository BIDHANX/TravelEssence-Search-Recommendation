-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 17, 2024 at 04:59 PM
-- Server version: 10.4.24-MariaDB
-- PHP Version: 8.1.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `travel_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

CREATE TABLE `bookings` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `destination_id` int(11) DEFAULT NULL,
  `status` enum('Pending','Approved','Declined') DEFAULT 'Pending',
  `is_pending` tinyint(1) DEFAULT 1,
  `booking_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `bookings`
--

INSERT INTO `bookings` (`id`, `user_id`, `destination_id`, `status`, `is_pending`, `booking_date`) VALUES
(84, 8, 22, 'Approved', 1, NULL),
(85, 8, 25, 'Approved', 1, NULL),
(86, 8, 26, 'Declined', 1, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `destinations`
--

CREATE TABLE `destinations` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `image` varchar(255) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `best_season` varchar(50) DEFAULT NULL,
  `ticket_price` decimal(10,2) DEFAULT NULL,
  `activities` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `destinations`
--

INSERT INTO `destinations` (`id`, `name`, `description`, `image`, `address`, `category`, `best_season`, `ticket_price`, `activities`) VALUES
(22, 'MountEverest', 'Mount Everest, known locally as Sagarmatha or Qomolangma is Earth\'s highest mountain above sea level, located in the Mahalangur Himal sub-range of the Himalayas. The China–Nepal border runs across its summit point. Its elevation (snow height) of 8,848.86 m (29,031 ft 8+1⁄2 in) was most recently established in 2020 by the Chinese and Nepali authorities.', 'mtt.jpg', 'Nepal', 'Natural', 'Winter', '1000.00', 'A short hike to the foot of Mount Everest, the highest point you can reach without technical climbing. You can also visit Kala Patthar, a rocky peak with panoramic views of Everest'),
(23, 'MountK2', 'K2 is the world’s second highest peak (28,251 feet [8,611 meters]), second only to Mount Everest. K2 is located in the Karakoram Range and lies partly in a Chinese-administered enclave of the Kashmir region within the Uygur Autonomous Region of Xinjiang, China, and partly in the Gilgit-Baltistan portion of Kashmir under the administration of Pakistan.', 'k2.jpg', 'pakistan', 'Natural', 'Winter', '700.00', 'mountaineering, the sport of attaining, or attempting to attain, high points in mountainous regions, mainly for the pleasure of the climb..'),
(24, 'Rara Lake', 'Rara Lake, also known as Mahendra Lake, is the largest fresh water lake in the Nepalese Himalayas. It is the main feature of Rara National Park, located in Jumla and Mugu Districts of Karnali Province. Rara National Park stretches over 106 km².', 'rara.jpg', 'Nepal', 'Natural', 'spring season from March through May', '20.00', 'Boating and '),
(25, 'Bhaktapur', 'Bhaktapur Durbar Square is a former royal palace complex in Bhaktapur, Nepal. It hosted the Malla rulers of Nepal from the 14th to the 15th century, as well as the kings of the country of Bhaktapur from the 15th to late 18th century, until the country was conquered in 1769', 'Bhaktapur.jpg', 'Nepal', 'Historical', 'Every Season', '5.00', '\"Bhaktapur Durbar Square,\" as the city is often called, is a museum of medieval art and architecture with many specimens of sculpture, woodcarving, and huge pagoda temples dedicated to different gods and goddesses.'),
(26, 'paris', 'Paris is France\'s capital and the focal point of French politics, economics, culture, and business. It is the world\'s fourth largest city, with 20 districts. Paris has a much higher population density than the surrounding provinces in Greater Paris.', 'parsi.jpg', 'France', 'Beautiful Architecture', 'Spring ', '3000.00', 'Picnic in the park, Walk along the Seine'),
(27, 'Basantapur', 'Bangkok, Thailand’s capital, is a large city known for ornate shrines and vibrant street life. The boat-filled Chao Phraya River feeds its network of canals, flowing past the Rattanakosin royal district, home to opulent Grand Palace and its sacred Wat Phra Kaew Temple.', 'bak.jpg', 'Thailand', 'Historical', 'winter', '200.00', 'Clubing');

-- --------------------------------------------------------

--
-- Table structure for table `profiles`
--

CREATE TABLE `profiles` (
  `user_id` int(11) NOT NULL,
  `profile_image` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('user','admin') NOT NULL DEFAULT 'user',
  `email` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `role`, `email`) VALUES
(2, 'sonam', '$pbkdf2-sha256$29000$9N57z/l/T0lJ6V0r5fwfIw$e6s/bFIg6bbGjFVUxkC3SKznb2fmbQ49oEYi1.lOa2A', 'user', 'sonam@gmail.com'),
(3, 'bidhan', '$pbkdf2-sha256$29000$eY/x/n.v1TpnjFHKOYfQOg$CC19XIJjtho.cI2VP0Upzp9cxD3WeKnQVDmtJo056h8', 'admin', 'bidhan@gmail.com'),
(4, 'milan', '$pbkdf2-sha256$29000$Zexdq5VSqvW.F6JUivG.tw$J3cwenek2XStgJ90MHAtLJ3bo0Kub6sa.3ABfmdA5sk', 'user', 'mi@gmail.com'),
(8, 'ram', '$pbkdf2-sha256$29000$DcGYc66V8n5vLYXwfq.1tg$wOxfl0kMmr2tGl8btaNqC2CCEs.3W0Y6YFvJYmTEk5U', 'user', 'ram12@gmail.com');

-- --------------------------------------------------------

--
-- Table structure for table `wishlist`
--

CREATE TABLE `wishlist` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `destination_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bookings`
--
ALTER TABLE `bookings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `bookings_ibfk_2` (`destination_id`);

--
-- Indexes for table `destinations`
--
ALTER TABLE `destinations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `profiles`
--
ALTER TABLE `profiles`
  ADD PRIMARY KEY (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `wishlist`
--
ALTER TABLE `wishlist`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`,`destination_id`),
  ADD KEY `destination_id` (`destination_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bookings`
--
ALTER TABLE `bookings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=87;

--
-- AUTO_INCREMENT for table `destinations`
--
ALTER TABLE `destinations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `wishlist`
--
ALTER TABLE `wishlist`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bookings`
--
ALTER TABLE `bookings`
  ADD CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`destination_id`) REFERENCES `destinations` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `profiles`
--
ALTER TABLE `profiles`
  ADD CONSTRAINT `profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `wishlist`
--
ALTER TABLE `wishlist`
  ADD CONSTRAINT `wishlist_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `wishlist_ibfk_2` FOREIGN KEY (`destination_id`) REFERENCES `destinations` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
