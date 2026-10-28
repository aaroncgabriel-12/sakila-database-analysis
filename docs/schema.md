
# Rental workflow and schema notes

Module 3 framed the sample business as **Sakila Videoz**, a small rental chain
interested in stocking decisions, revenue, and customer retention. Its relationship
discussion focused on the seven tables below. The database and schema originate
with Oracle's Sakila sample; this is a project-specific explanation of that model.

| Table | Role | Selected foreign-key relationships |
| --- | --- | --- |
| `film` | Catalog titles and attributes | Language references are outside this simplified workflow |
| `inventory` | A physical copy of a film at a store | `film_id → film.film_id`; `store_id → store.store_id` |
| `rental` | A customer rents a specific inventory copy | `inventory_id → inventory.inventory_id`; `customer_id → customer.customer_id`; `staff_id → staff.staff_id` |
| `payment` | Amount paid by a customer, with a possible rental link | `customer_id → customer.customer_id`; `staff_id → staff.staff_id`; `rental_id → rental.rental_id` |
| `customer` | A sample customer associated with a store | `store_id → store.store_id` |
| `store` | Rental location | `manager_staff_id → staff.staff_id` |
| `staff` | Staff member associated with a store | `store_id → store.store_id` |

Separating `film` from `inventory` distinguishes a title from individual copies.
`rental` links those copies to customers and staff; `payment` records amounts.
Address, city, country, language, actor, and category tables extend the model.
The notebook's store-location query follows `store → address → city`; its actor
query uses `actor → film_actor → film_category` and the total category count.

The Module 4 queries analyze catalog ratings, inventory coverage, store cities,
and actor category coverage. They do not compute rental revenue, customer
retention, staff performance, or stock recommendations. Those remain possible
extensions motivated by the Module 3 discussion.

Read the [official schema documentation](https://dev.mysql.com/doc/sakila/en/sakila-structure.html)
for complete columns, types, constraints, and tables. No original course diagram,
worksheet, customer records, or database dump is bundled here.
