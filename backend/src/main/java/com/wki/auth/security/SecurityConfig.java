package com.wki.auth.security;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.HttpStatusEntryPoint;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;
import java.util.List;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

        @Bean
        public PasswordEncoder passwordEncoder() {
                return new BCryptPasswordEncoder();
        }

        @Bean
        public SecurityFilterChain filterChain(
                        HttpSecurity http,
                        JwtAuthFilter jwtFilter) throws Exception {

                http
                                .csrf(AbstractHttpConfigurer::disable)
                                .cors(Customizer.withDefaults())

                                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))

                                .exceptionHandling(e -> e.authenticationEntryPoint(
                                                new HttpStatusEntryPoint(HttpStatus.UNAUTHORIZED)))

                                .authorizeHttpRequests(a -> a

                                                // Allow OPTIONS requests
                                                .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()

                                                // Public frontend pages
                                                .requestMatchers(
                                                                "/",
                                                                "/index.html",
                                                                "/login.html",
                                                                "/register.html",
                                                                "/employee-dashboard.html",
                                                                "/dept-head-dashboard.html",
                                                                "/hr-dashboard.html",
                                                                "/manager-dashboard.html",
                                                                "/trainer-dashboard.html",
                                                                "/css/**",
                                                                "/js/**",
                                                                "/favicon.ico")
                                                .permitAll()

                                                // Public authentication APIs
                                                .requestMatchers("/api/auth/**").permitAll()

                                                // Protected API endpoints
                                                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                                                .requestMatchers("/api/employee/**").hasRole("EMPLOYEE")
                                                .requestMatchers("/api/dept-head/**").hasRole("DEPT_HEAD")

                                                // All remaining requests require authentication
                                                .anyRequest().authenticated())

                                .addFilterBefore(
                                                jwtFilter,
                                                UsernamePasswordAuthenticationFilter.class);

                return http.build();
        }

        @Bean
        public CorsConfigurationSource corsConfigurationSource(
                        @Value("${app.cors.allowed-origins}") String origins) {

                CorsConfiguration cfg = new CorsConfiguration();

                cfg.setAllowedOrigins(
                                Arrays.stream(origins.split(","))
                                                .map(String::trim)
                                                .toList());

                cfg.setAllowedMethods(
                                List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));

                cfg.setAllowedHeaders(
                                List.of("Authorization", "Content-Type"));

                UrlBasedCorsConfigurationSource src = new UrlBasedCorsConfigurationSource();

                src.registerCorsConfiguration("/api/**", cfg);

                return src;
        }
}