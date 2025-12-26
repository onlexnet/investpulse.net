package net.investpulse.configserver;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.config.server.EnableConfigServer;

@SpringBootApplication
@EnableConfigServer
public class Program {

	public static void main(String[] args) {
		SpringApplication.run(Program.class, args);
	}

}
