-- Sakila analysis queries extracted unchanged from the original coursework.
-- Run against an existing Sakila sample database; these statements are read-only.

-- query: films_by_rating
-- How many titles are in each film rating?
SELECT rating, COUNT(*) AS film_count
FROM film
GROUP BY rating
ORDER BY film_count DESC;

-- query: distinct_films_in_stock
-- How many distinct titles have inventory records, by rating?
SELECT f.rating, COUNT(DISTINCT i.film_id) AS distinct_films_in_stock
FROM inventory i
JOIN film f ON f.film_id = i.film_id
GROUP BY f.rating
ORDER BY distinct_films_in_stock DESC;

-- query: films_unavailable
-- How many titles have no inventory records?
SELECT COUNT(*) AS films_unavailable
FROM film f
LEFT JOIN inventory i ON f.film_id = i.film_id
WHERE i.film_id is NULL;

-- query: store_cities
-- In which cities are stores located?
SELECT DISTINCT c.city
FROM store s
JOIN address a ON s.address_id = a.address_id
JOIN city c ON a.city_id = c.city_id
ORDER BY c.city;

-- query: top_actor_all_categories
-- Which actor appearing in every category has the most distinct films?
SELECT 
    a.actor_id,
    a.first_name,
    a.last_name,
    COUNT(DISTINCT fa.film_id) AS film_count
FROM actor a
JOIN film_actor fa ON a.actor_id = fa.actor_id
JOIN film_category fc ON fa.film_id = fc.film_id
GROUP BY a.actor_Id, a.first_name, a.last_name
HAVING COUNT(DISTINCT fc.category_id) = (SELECT COUNT(*)FROM category)
ORDER BY film_count DESC
LIMIT 1;
