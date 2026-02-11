/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-12.1.2-MariaDB, for osx10.20 (arm64)
--
-- Host: localhost    Database: rastreo_gps
-- ------------------------------------------------------
-- Server version	8.4.4

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `bitacora_rutas`
--

DROP TABLE IF EXISTS `bitacora_rutas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `bitacora_rutas` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `device_id_fk` int DEFAULT NULL,
  `latitud` decimal(10,8) NOT NULL,
  `longitud` decimal(11,8) NOT NULL,
  `bateria_nivel` tinyint DEFAULT NULL,
  `fecha_reporte` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_dispositivo` (`device_id_fk`),
  CONSTRAINT `fk_dispositivo` FOREIGN KEY (`device_id_fk`) REFERENCES `cat_dispositivos` (`id_interno`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1531 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cat_dispositivos`
--

DROP TABLE IF EXISTS `cat_dispositivos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cat_dispositivos` (
  `id_interno` int NOT NULL AUTO_INCREMENT,
  `serial_traccar` varchar(50) NOT NULL,
  `nombre_asignado` varchar(100) DEFAULT 'Sin Nombre',
  `placa_vehiculo` varchar(20) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_interno`),
  UNIQUE KEY `serial_traccar` (`serial_traccar`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `vista_monitoreo`
--

DROP TABLE IF EXISTS `vista_monitoreo`;
/*!50001 DROP VIEW IF EXISTS `vista_monitoreo`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `vista_monitoreo` AS SELECT
 1 AS `nombre_asignado`,
  1 AS `placa_vehiculo`,
  1 AS `latitud`,
  1 AS `longitud`,
  1 AS `bateria`,
  1 AS `fecha_reporte` */;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `vista_monitoreo`
--

/*!50001 DROP VIEW IF EXISTS `vista_monitoreo`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`usuario_gps`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_monitoreo` AS select `d`.`nombre_asignado` AS `nombre_asignado`,`d`.`placa_vehiculo` AS `placa_vehiculo`,`b`.`latitud` AS `latitud`,`b`.`longitud` AS `longitud`,concat(`b`.`bateria_nivel`,'%') AS `bateria`,`b`.`fecha_reporte` AS `fecha_reporte` from (`bitacora_rutas` `b` join `cat_dispositivos` `d` on((`b`.`device_id_fk` = `d`.`id_interno`))) order by `b`.`fecha_reporte` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-02-11 15:20:27
